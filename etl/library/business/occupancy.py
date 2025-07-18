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
    beds     = 0.0 # Total beds
    beds_c   = 0.0 # Consolidated beds
    beds_cnv = 0.0 # Convertible beds
    beds_pot = 0.0 # Potential beds
    beds_pre = 0.0 # Pre capex beds
    beds_cap = 0.0 # Capex beds
    avail    = 0.0 # Available room nights
    convert  = ''

    # Date
    date = row['date']

    # Building not active
    if date < row['Start_date']:
      return [beds, beds_c, beds_cnv, beds_pot, beds_pre, beds_cap, avail, convert, 0, 0, 0]

    # Resource not existent
    if row['Date_from'] and row['Date_to']:
      if row['Date_from'] <= date <= row['Date_to']:
        return [beds, beds_c, beds_cnv, beds_pot, beds_pre, beds_cap, avail, convert, 0, 0, 0]

    # All flat non availability rows
    availability = df_avail[df_avail['Resource_id'] == row['flat']]
    for _, r in availability.iterrows():

      # Bed is not available?
      if r['Date_from'] <= date <= r['Date_to']:
        # Convertible
        convert = r['Convertible'] or 'N/D'

        # Potential
        if r['Status_id'] == 2:
          beds_pot = 1.0
          if convert in ('LTC', 'FTC'):
            beds_cnv = 1.0

        # Pre capex
        if r['Status_id'] == 3:
          convert  = 'PRECAPEX'
          beds_pot = 1.0
          beds_cnv = 1.0
          beds_pre = 1.0

        # Capex
        if r['Status_id'] == 4:
          convert  = 'CAPEX'
          beds_pot = 1.0
          beds_cnv = 1.0
          beds_cap = 1.0

        return [beds, beds_c, beds_cnv, beds_pot, beds_pre, beds_cap, avail, convert, 0, 0, 0]

    # Bed is available (and convertible, and potential)
    beds     = 1.0
    beds_c   = 1.0
    beds_pot = 1.0
    beds_cnv = 1.0
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
    return [beds, beds_c, beds_cnv, beds_pot, beds_pre, beds_cap, avail, convert, 0, 0, 0]
  

  # Log
  logger.info('Calculating beds...')

  # Connection
  con = dbClient.getconn()

  # Existing resources
  sql = '''
  -- All places
  SELECT r.id, r."Code" AS "resource", r."Flat_id" AS "flat", b."Start_date",
  r."Pre_capex_long_term" AS "val_current",
  r."Post_capex" AS "val_residential",
  r."Post_capex" AS "val_cosharing",
  ra."Date_from",
  ra."Date_to",
  CASE
    WHEN r."Billing_type" = 'mes' THEN 'Monthly' 
    WHEN r."Billing_type" = 'quincena' THEN 'Fortnightly' 
    WHEN r."Billing_type" = 'proporcional' THEN 'Daily' 
  END AS "type"
  FROM "Resource"."Resource" r 
  INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
  LEFT JOIN "Resource"."Resource_availability" ra ON (r.id = ra."Resource_id" OR r."Room_id" = ra."Resource_id") AND ra."Status_id" = 5 
  WHERE r."Resource_type" = 'plaza'
  
  UNION
  
  -- All rooms without places
  SELECT r.id, r."Code" AS "resource", r."Flat_id" AS "flat", b."Start_date", 
  r."Pre_capex_long_term" AS "val_current",
  r."Post_capex" AS "val_residential",
  r."Post_capex" AS "val_cosharing",
  ra."Date_from",
  ra."Date_to",
  CASE
    WHEN r."Billing_type" = 'mes' THEN 'Monthly' 
    WHEN r."Billing_type" = 'quincena' THEN 'Fortnightly' 
    WHEN r."Billing_type" = 'proporcional' THEN 'Daily' 
  END AS "type"
  FROM "Resource"."Resource" r 
  INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
  LEFT JOIN "Resource"."Resource_availability" ra ON (r.id = ra."Resource_id" OR r."Room_id" = ra."Resource_id") AND ra."Status_id" = 5 
  WHERE "Resource_type" = 'habitacion' AND 
  NOT EXISTS (SELECT id FROM "Resource"."Resource" rr WHERE rr."Room_id" = r.id)
  
  UNION
  
  -- All Flats without rooms
  SELECT r.id, r."Code" AS "resource", r.id AS "flat", b."Start_date",
  r."Pre_capex_long_term" AS "val_current",
  r."Post_capex" AS "val_residential",
  r."Post_capex" AS "val_cosharing",
  ra."Date_from",
  ra."Date_to",
  CASE
    WHEN r."Billing_type" = 'mes' THEN 'Monthly' 
    WHEN r."Billing_type" = 'quincena' THEN 'Fortnightly' 
    WHEN r."Billing_type" = 'proporcional' THEN 'Daily' 
  END AS "type"
  FROM "Resource"."Resource" r 
  LEFT JOIN "Resource"."Resource_availability" ra ON (r.id = ra."Resource_id" OR r."Room_id" = ra."Resource_id") AND ra."Status_id" = 5 
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
  SELECT "Resource_id", "Date_from", "Date_to", "Status_id", "Convertible", "Not_flat"
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
  df_beds[['beds', 'beds_c', 'beds_cnv', 'beds_pot', 'beds_pre', 'beds_cap', 'available', 'convertible', 'val_current', 'val_residential', 'val_cosharing', ]] = df_beds.apply(count, axis=1, result_type='expand')
  logger.info('- Beds and available nights calculated')

  # To CSV
  df_beds['id'] = range(1, 1 + len(df_beds))
  df_beds['data_type'] = 'Real'
  df_beds.to_csv('csv/beds_real.csv', index=False, sep=',', encoding='utf-8', columns=['id', 'data_type', 'resource', 'date', 'beds', 'beds_c', 'beds_cnv', 'beds_pot', 'beds_pre', 'beds_cap', 'available', 'convertible','val_current','val_residential','val_cosharing'])  
  logger.info('- Beds saved')


# ###################################################
# Calculate occupancy
# ###################################################

def occupancy(dbClient):

  def nights(row):
    # First and last days of the month
    date  = row['date']
    days  = calendar.monthrange(date.year, date.month)[1]
    mfrom = date.replace(day=1)
    mto   = date + relativedelta(days=days-1)

    # Special locks?
    availability = df_avail[df_avail['id'] == row['id']]
    for _, r in availability.iterrows():
      if (r['Date_from'] <= mfrom <= mto <= r['Date_to']):
        #print(row['resource'], r['Date_to'], r['Date_from'], row['Date_to'], row['Date_from'])
        return [0, 0, 0, 0]

    # Calc booked nights
    xfrom = max(mfrom, row['Date_from'])
    xto   = min(mto, row['Date_to'])
    occu  = 1 + (xto - xfrom).days

    # Type
    type = row['Billing_type']
    if xto < mto:
      type = row['Billing_type_last']
    if type == 'proporcional':
      sold = occu
    elif type == 'quincena':
      if xto.day < 16 or xfrom.day > 15:
        sold = 15
      else:
        sold = days
    else:
      sold = days    

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
        COALESCE(b."Booking_id", b."Booking_group_id") AS "booking",
        r.id,
        r."Code" AS "resource",
        dr.date,
        b."Date_from",
        b."Date_to",
        b."Billing_type",
        b."Billing_type_last",
        CASE 
          WHEN b."Status" IN ('confirmada', 'grupobloqueado') THEN 'Tentative' 
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
    WHERE (b."Booking_id" IS NOT NULL OR b."Booking_group_id" IS NOT NULL)
      AND b."Status" NOT IN ('pendientepago')
      AND b."Date_from" <= '{END_DATE}'
      AND b."Date_to" >= '{START_DATE}'
    ORDER BY 3, 1
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

  # Special locks
  sql = '''
  SELECT r.id, r."Code", bd."Date_from", bd."Date_to"
  FROM "Booking"."Booking_detail" bd
    INNER JOIN "Resource"."Resource" r ON r.id = bd."Resource_id"
    INNER JOIN "Resource"."Resource_availability" ra ON ra.id = bd."Availability_id"
    INNER JOIN "Resource"."Resource_status" rs ON rs.id = ra."Status_id"
  WHERE rs."Not_flat"
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
  logger.info('- Special locks retrieved')

  # Ocuppied and sold nights
  df_books[['occupied', 'occupied_t', 'sold', 'sold_t']] = df_books.apply(nights, axis=1, result_type='expand')
  logger.info('- Occupied and sold nights calculated')

  # Additional columns
  df_books = df_books.reset_index(drop=True)
  df_books['id'] = (df_books.index + 1).astype(str).str.zfill(7)
  df_books['data_type'] = 'Real'

  # To CSV
  df_books.to_csv('csv/occupancy_real.csv', index=False, sep=',', encoding='utf-8', columns=['id', 'data_type', 'resource', 'date', 'occupied', 'sold', 'occupied_t', 'sold_t', 'booking', 'stay_length'])
  logger.info('- Occupancy saved')