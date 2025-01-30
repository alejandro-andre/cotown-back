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
# Constants
# ###################################################

START_DATE = '2024-01-01'
END_DATE   = '2029-12-31'


# ###################################################
# Calculate total and available beds
# ###################################################

def beds(dbClient):

  def count(row):
    # Counters
    beds   = 0.0 # Total beds
    beds_c = 0.0 # Consolidated beds
    beds_p = 0.0 # Potential beds
    beds_x = 0.0 # Capex beds
    avail  = 0.0 # Available room nights

    # Date
    date = row['date']

    # Building started?
    if date < row['Start_date']:
      return [beds, beds_c, beds_p, beds_x, avail]

    # All flat non availability rows
    availability = df_avail[df_avail['Resource_id'] == row['flat']]

    # Bed is not available?
    for _, r in availability.iterrows():
      if r['Date_from'] <= date <= r['Date_to']:
        # Potential
        if r['Status_id'] == 2:
          beds_p = 1.0
        # Precapex + Capex
        if r['Status_id'] in (3, 4):
          beds_x = 1.0
        return [beds, beds_c, beds_p, beds_x, avail]

    # Bed is available
    beds = 1.0
    beds_c = 1.0
    avail = calendar.monthrange(date.year, date.month)[1]

    # Consolidated date
    c_date = date
    if date.month >= 11: 
      c_date = date.replace(month=10)
    elif date.month >= 3: 
      c_date = date.replace(month=2)

    # Not available on consolidated date?
    for _, r in availability.iterrows():
      if r['Date_from'] <= c_date <= r['Date_to']:
        beds_c = 0.5
    
    # Return values
    return [beds, beds_c, beds_p, beds_x, avail]
  

  # Log
  logger.info('Calculating beds...')

  # Connection
  con = dbClient.getconn()

  # Existing resources
  sql = '''
  -- All places
  SELECT r.id, r."Code" AS "resource", r."Flat_id" AS "flat", b."Start_date",
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
  SELECT r.id, r."Code" AS "resource", r."Flat_id" AS "flat", b."Start_date", 
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
  SELECT r.id, r."Code" AS "resource", r.id AS "flat", b."Start_date",
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
  SELECT "Resource_id", "Date_from", "Date_to", "Status_id"
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

  # Dates
  df_dates = pd.DataFrame({'date': [date.date() for date in pd.date_range(start=START_DATE, end=END_DATE, freq='MS')]})

  # Resources x dates Cross table
  df_dates['key'] = 1
  df_res['key'] = 1
  df_beds = pd.merge(df_res, df_dates, on='key').drop('key', axis=1)

  # Beds and available nights
  df_beds[['beds','beds_c','beds_p','beds_x','available',]] = df_beds.apply(count, axis=1, result_type='expand')
  df_beds = df_beds.query("not (beds == 0.0 and beds_c == 0.0 and beds_p == 0.0 and beds_x == 0.0)")
  logger.info('- Beds and available nights calculated')

  # To CSV
  df_beds['id'] = range(1, 1 + len(df_beds))
  df_beds['data_type'] = 'Real'
  df_beds.to_csv('csv/beds_real.csv', index=False, sep=',', encoding='utf-8', columns=['id', 'data_type', 'resource', 'date', 'beds', 'beds_c', 'beds_p', 'beds_x', 'available'])
  logger.info('- Beds saved')


# ###################################################
# Calculate occupancy
# ###################################################

def occupancy(dbClient):

  def nights(row):
    # First and last days of the month
    date = row['date']
    mfrom = date.replace(day=1)
    mto = date + relativedelta(months=1) - relativedelta(days=1)
   
    # Sum booked nights
    occu = 1 + (min(mto, row['Date_to']) - max(mfrom, row['Date_from'])).days
    type = row['Billing_type']
    if type == 'proporcional':
      sold = occu
    elif type == 'quincena':
      if occu < 15:
        sold = 15
      else:
        sold = calendar.monthrange(date.year, date.month)[1]
    else:
      sold = calendar.monthrange(date.year, date.month)[1]

    # Update
    return [
      occu if row['data_type'] == 'Real' else 0, 
      occu if row['data_type'] == 'Tentative' else 0, 
      sold if row['data_type'] == 'Real' else 0, 
      sold if row['data_type'] == 'Tentative' else 0
    ]


  # Log
  logger.info('Calculating occupancy...')

  # Connection
  con = dbClient.getconn()

  # Bookings
  sql = f'''
    WITH date_range AS (
      SELECT generate_series('{START_DATE}', '{END_DATE}', interval '1 month')::date AS "date"
    )
    SELECT
        b.id AS "booking",
        r."Code" AS "resource",
        dr.date,
        b."Date_from",
        b."Date_to",
        b."Billing_type",
        CASE 
          WHEN b."Status" IN ('pendientepago', 'grupobloqueado') THEN 'Tentative' 
          ELSE 'Real' 
        END AS "data_type",
        CASE
          WHEN b."Booking_group_id" IS NOT NULL THEN 'GROUP'
          WHEN EXTRACT(MONTH FROM AGE(b."Date_to", b."Date_from")) < 3 THEN 'SHORT'
          WHEN EXTRACT(MONTH FROM AGE(b."Date_to", b."Date_from")) < 7 THEN 'MEDIUM'
          ELSE 'LONG'
        END AS "stay_length"
    FROM "Booking"."Booking_detail" b
    INNER JOIN (
        SELECT r."Code", r.id
        FROM "Resource"."Resource" r
        WHERE NOT EXISTS ( SELECT id FROM "Resource"."Resource" rr WHERE rr."Code" LIKE CONCAT(r."Code", '.%') )
    ) AS r ON r.id = b."Resource_id"
    INNER JOIN date_range dr ON dr.date BETWEEN DATE_TRUNC('month', b."Date_from") AND b."Date_to"
    WHERE b."Availability_id" IS NULL
      AND b."Date_from" <= '{END_DATE}'
      AND b."Date_to" >= '{START_DATE}'
    ORDER BY 1 DESC, 3
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
  logger.info('- Bookings x month retrieved')

  # Ocuppied and sold nights
  df_books[['occupied','occupied_t','sold','sold_t']] = df_books.apply(nights, axis=1, result_type='expand')
  logger.info('- Occupied and sold nights calculated')

  # Additional columns
  df_books = df_books.reset_index(drop=True)
  df_books['id'] = (df_books.index + 1).astype(str).str.zfill(7)
  df_books['data_type'] = 'Real'

  # To CSV
  df_books.to_csv('csv/occupancy_real.csv', index=False, sep=',', encoding='utf-8', columns=['id', 'data_type', 'resource', 'date', 'occupied', 'sold', 'occupied_t', 'sold_t', 'booking', 'stay_length'])
  logger.info('- Occupancy saved')