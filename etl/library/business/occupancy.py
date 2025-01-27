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

  def nights(resource, type, date, data_type):
    # First and last days of the month
    mfrom = date.replace(day=1)
    mto = date + relativedelta(months=1) - relativedelta(days=1)
   
    # All bookings for the resource
    rows = df_books[(df_books['resource'] == resource) & (df_books['data_type'] == data_type)]

    # Sum booked nights
    n = 0
    for _, row in rows.iterrows():
      dfrom = row['Date_from']
      dto = row['Date_to']
      if dto >= mfrom and dfrom <= mto:
        n = n + 1 + (min(mto, dto) - max(mfrom, dfrom)).days
        if type == 'Monthly':
          n = calendar.monthrange(date.year, date.month)[1]
        if type == 'Fortnightly':
          if n < 15:
            n = 15
          else:
            n = calendar.monthrange(date.year, date.month)[1]
    return n


  def beds(resource, date):
    # All flat non availability rows
    rows = df_avail[df_avail['Resource_id'] == resource]

    # Not available
    for _, row in rows.iterrows():
      if row['Date_from'] <= date <= row['Date_to']:
        return [0.0, 0.0]
      
    # Consolidated date
    c_date = date
    if date.month >= 11: c_date = date.replace(month=10)
    elif date.month >= 3: c_date = date.replace(month=2)
    for _, row in rows.iterrows():
      if row['Date_from'] <= c_date <= row['Date_to']:
        return [1.0, 0.5]
      
    # Beds = Consolidated beds
    return [1.0, 1.0]
  
  
  def available(id, date, rooms=False):
    # All flat non availability rows
    rows = df_avail[df_avail['Resource_id'] == id]

    # Check if the date is in between any range
    for _, row in rows.iterrows():
      if row['Date_from'] <= date <= row['Date_to']:
        return 0
    return calendar.monthrange(date.year, date.month)[1]
  

  # Log
  logger.info('Calculating occupancy...')

  # Connection
  con = dbClient.getconn()

  # Existing resources
  sql = '''
  -- All places
  SELECT r.id, r."Code" AS "resource", r."Flat_id" AS "flat", 
  CASE
    WHEN r."Billing_type" = 'mes' THEN 'Monthly' 
    WHEN r."Billing_type" = 'quincena' THEN 'Fortnightly' 
    WHEN r."Billing_type" = 'proporcional' THEN 'Daily' 
  END AS "type"
  FROM "Resource"."Resource" r 
  INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
  WHERE r."Resource_type" = 'plaza'
  
  UNION
  
  -- All rooms without places
  SELECT r.id, r."Code" AS "resource", r."Flat_id" AS "flat", 
  CASE
    WHEN r."Billing_type" = 'mes' THEN 'Monthly' 
    WHEN r."Billing_type" = 'quincena' THEN 'Fortnightly' 
    WHEN r."Billing_type" = 'proporcional' THEN 'Daily' 
  END AS "type"
  FROM "Resource"."Resource" r 
  INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
  WHERE "Resource_type" = 'habitacion' AND 
  NOT EXISTS (SELECT id FROM "Resource"."Resource" rr WHERE rr."Room_id" = r.id)
  
  UNION
  
  -- All Flats without rooms
  SELECT r.id, r."Code" AS "resource", r.id AS "flat", 
  CASE
    WHEN r."Billing_type" = 'mes' THEN 'Monthly' 
    WHEN r."Billing_type" = 'quincena' THEN 'Fortnightly' 
    WHEN r."Billing_type" = 'proporcional' THEN 'Daily' 
  END AS "type"
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
  SELECT 
    r."Code" AS "resource", 
    b."Date_from", 
    b."Date_to",
    b."Billing_type",
    CASE
      WHEN b."Status" IN ('pendientepago', 'grupobloqueado') THEN 'Tentative'
      ELSE 'Real'
    END AS "data_type"
  FROM "Booking"."Booking_detail" b
  INNER JOIN (
    SELECT r."Code", r.id
    FROM "Resource"."Resource" r
    INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
    WHERE NOT EXISTS (SELECT id FROM "Resource"."Resource" rr WHERE rr."Code" LIKE CONCAT(r."Code", '.%'))
    ) AS r ON r.id = b."Resource_id"
  WHERE b."Availability_id" IS NULL
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

  # Dates
  start_date = '2024-01-01'
  end_date   = '2026-12-31'
  df_dates = pd.DataFrame({'date': [date.date() for date in pd.date_range(start=start_date, end=end_date, freq='MS')]})

  # Resources x dates Cross table
  df_dates['key'] = 1
  df_res['key'] = 1
  df_cross = pd.merge(df_res, df_dates, on='key').drop('key', axis=1)

  # Beds and consolidated beds
  df_cross[['beds', 'beds_c']] = df_cross.apply(lambda row: beds(row['flat'], row['date']), axis=1, result_type='expand')
  logger.info('- Beds calculated')

  # Available nights
  df_cross['available'] = df_cross.apply(lambda row: available(row['flat'], row['date']), axis=1)
  logger.info('- Available nights calculated')

  # Ocuppied nights
  df_cross['occupied'] = df_cross.apply(lambda row: nights(row['resource'], None, row['date'], 'Real'), axis=1)
  df_cross['occupied_t'] = df_cross.apply(lambda row: nights(row['resource'], None, row['date'], 'Tentative'), axis=1)
  logger.info('- Occupied nights calculated')

  # Sold nights
  df_cross['sold'] = df_cross.apply(lambda row: nights(row['resource'], row['type'], row['date'], 'Real'), axis=1)
  df_cross['sold_t'] = df_cross.apply(lambda row: nights(row['resource'], row['type'], row['date'], 'Tentative'), axis=1)
  logger.info('- Sold nights calculated')

  # Additional columns
  df_cross['booking'] = ''
  df_cross['stay_length'] = ''
  
  # To CSV
  df_cross['id'] = range(1, 1 + len(df_cross))
  df_cross['data_type'] = 'Real'
  df_cross.to_csv('csv/occupancy_real.csv', index=False, sep=',', encoding='utf-8', columns=['id', 'data_type', 'resource', 'date', 'beds', 'beds_c', 'available', 'occupied', 'sold', 'occupied_t', 'sold_t', 'booking', 'stay_length'])
  df_cross.to_csv('csv/beds_real.csv', index=False, sep=',', encoding='utf-8', columns=['id', 'data_type', 'resource', 'date', 'beds', 'beds_c', 'available'])

  # Log
  logger.info('Done')