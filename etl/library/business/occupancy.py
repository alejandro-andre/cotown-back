# ###################################################
# Imports
# ###################################################

# System includes
import calendar
import pandas as pd
from dateutil.relativedelta import relativedelta

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Calculate availability
# ###################################################


def occupancy(dbClient):

  def nights(resource, type, date):

    # First and last days of the month
    mfrom = date.replace(day=1)
    mto = date + relativedelta(months=1) - relativedelta(days=1)
   
    # All bookings for the resource
    rows = df_books[df_books['resource'] == resource]

    # Sum booked nights
    n = 0
    for _, row in rows.iterrows():
      dfrom = row['Date_from']
      dto = row['Date_to']
      if dto >= mfrom and dfrom <= mto:
        n = n + 1 + (min(mto, dto) - max(mfrom, dfrom)).days
        if type == 'quincena':
          if n < 15:
            n = 15
          else:
            n = calendar.monthrange(date.year, date.month)[1]
        if type == 'mes':
          n = calendar.monthrange(date.year, date.month)[1]
    return n


  def available(flat, date):

    # All flat non availability rows
    rows = df_avail[df_avail['Resource_id'] == flat]

    # Check if the date is in between any range
    for _, row in rows.iterrows():
      if row['Date_from'] <= date <= row['Date_to']:
        return 0  # Not available
      
    # Available days that month
    return calendar.monthrange(date.year, date.month)[1]
  
  # Log
  logger.info('Calculating occupancy...')

  # Connection
  con = dbClient.getconn()

  # Dates interval
  start_date = '2024-01-01'
  end_date   = '2029-12-31'
  dates      = [date.date() for date in pd.date_range(start=start_date, end=end_date, freq='MS')][:-1]

  # Existing resources
  sql = '''
  -- All places
  SELECT r.id, r."Code" AS "resource", r."Flat_id", r."Billing_type" as "type"
  FROM "Resource"."Resource" r 
  INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
  WHERE r."Resource_type" = 'plaza'
  
  UNION
  
  -- All rooms without places
  SELECT r.id, r."Code" AS "resource", r."Flat_id", r."Billing_type" as "type"
  FROM "Resource"."Resource" r 
  INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
  WHERE "Resource_type" = 'habitacion' AND 
  NOT EXISTS (SELECT id FROM "Resource"."Resource" rr WHERE rr."Room_id" = r.id)
  
  UNION
  
  -- All Flats without rooms
  SELECT r.id, r."Code" AS "resource", r.id as "Flat_id", r."Billing_type" as "type"
  FROM "Resource"."Resource" r 
  INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
  WHERE "Resource_type" = 'piso' AND 
  NOT EXISTS (SELECT id FROM "Resource"."Resource" rr WHERE rr."Flat_id" = r.id)

  ORDER BY 2
  '''
  try:
    cur = dbClient.execute(con, sql)
    columns = [desc[0] for desc in cur.description]
    df_res = pd.DataFrame.from_records(cur.fetchall(), columns=columns)
  except Exception as e:
    logger.error(e)
    con.rollback()
    dbClient.putconn(con)
    return None
  finally:
    cur.close()
  logger.info('- Resources retrieved')

  # Availability each month
  sql = '''
  SELECT "Resource_id", "Date_from", "Date_to"
  FROM "Resource"."Resource_availability" ra
  INNER JOIN "Resource"."Resource_status" rs ON rs.id = ra."Status_id"
  WHERE NOT rs."Available"
  ORDER BY 1
  '''
  try:
    cur = dbClient.execute(con, sql)
    columns = [desc[0] for desc in cur.description]
    df_avail = pd.DataFrame.from_records(cur.fetchall(), columns=columns)
  except Exception as e:
    logger.error(e)
    con.rollback()
    dbClient.putconn(con)
    return None
  finally:
    cur.close()
  logger.info('- Unavailabilities retrieved')

  # Bookings
  sql = '''
  SELECT r."Code" AS "resource", b."Date_from", b."Date_to"
  FROM "Booking"."Booking_detail" b
  INNER JOIN (
    SELECT r."Code", r.id
    FROM "Resource"."Resource" r
    INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
    WHERE NOT EXISTS (SELECT id FROM "Resource"."Resource" rr WHERE rr."Code" LIKE CONCAT(r."Code", '.%'))
    ) AS r ON r.id = b."Resource_id"
  WHERE b."Availability_id" IS NULL
    AND b."Status" NOT IN ('pendientepago', 'grupobloqueado')
  ORDER BY 1, 2, 3
  '''
  try:
    cur = dbClient.execute(con, sql)
    columns = [desc[0] for desc in cur.description]
    df_books = pd.DataFrame.from_records(cur.fetchall(), columns=columns)
  except Exception as e:
    logger.error(e)
    con.rollback()
    dbClient.putconn(con)
    return None
  finally:
    cur.close()
  logger.info('- Bookings retrieved')

  # Check available resources (beds) by month
  df_beds = df_res.copy()
  for dt in dates:
    df_beds[dt] = df_beds.apply(lambda row: available(row['Flat_id'], dt), axis=1)
  df_beds.drop('Flat_id', axis=1, inplace=True)
  df_res.drop('Flat_id', axis=1, inplace=True)
  logger.info('- Beds calculated')

  # Pivot booked room nights by month
  df_occupied = df_res.copy()
  for dt in dates:
    df_occupied[dt] = df_occupied.apply(lambda row: nights(row['resource'], None, dt), axis=1)
  logger.info('- Nights occupied calculated')

  # Pivot booked room nights by month
  df_sold = df_res.copy()
  for dt in dates:
    df_sold[dt] = df_sold.apply(lambda row: nights(row['resource'], row['type'], dt), axis=1)
  logger.info('- Nights sold calculated')

  # Reformat dataframes
  df_beds     = pd.melt(df_beds, id_vars=['id', 'resource', 'type'], var_name='date', value_name='available')
  df_occupied = pd.melt(df_occupied, id_vars=['id', 'resource', 'type'], var_name='date', value_name='occupied')
  df_sold     = pd.melt(df_sold, id_vars=['id', 'resource', 'type'], var_name='date', value_name='sold')
  df_final    = pd.merge(pd.merge(df_beds, df_occupied, on=['id', 'resource', 'type', 'date']), df_sold, on=['id', 'resource', 'type', 'date'])

  # Reindex
  df_final['id'] = range(1, 1 + len(df_final))
  df_final.set_index('id', inplace=True)

  # To CSV
  df_final.to_csv('csv/occupancy.csv', index=False, sep=',', encoding='utf-8', columns=['id', 'resource', 'date', 'available', 'occupied', 'sold'])

  # Log
  logger.info('Done')