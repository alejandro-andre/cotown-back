# ###################################################
# Imports
# ###################################################

# System includes
import calendar
import pandas as pd

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Custom includes
from library.business.constants import START_DATE, END_DATE


# ###################################################
# Calculate real beds
# ###################################################

def beds_real_calc(dbClient):

  def count_real(row):
    # Counters
    beds     = 0.0 # Available beds
    beds_cnv = 0.0 # Convertible beds
    beds_pot = 0.0 # Potential beds
    beds_pre = 0.0 # Pre capex beds
    beds_cap = 0.0 # Capex beds
    rn_avail = 0.0 # Available room nights
    rn_conv  = 0.0 # Convertible room nights
    convert  = ''

    # Date
    date = row['date']

    # Building not active
    if date < row['Start_date']:
      return [beds, beds_cnv, beds_pot, beds_pre, beds_cap, rn_avail, rn_conv, 0, 0, 0]

    # Resource not existent
    if row['Date_from'] and row['Date_to']:
      if row['Date_from'] <= date <= row['Date_to']:
        return [beds, beds_cnv, beds_pot, beds_pre, beds_cap, rn_avail, rn_conv, 0, 0, 0]

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
          if convert in ('N/D', 'LTC', 'FTC'):
            beds_cnv = 1.0
            rn_conv = calendar.monthrange(date.year, date.month)[1]

        # Pre capex
        if r['Status_id'] == 3:
          convert  = 'PRECAPEX'
          beds_pot = 1.0
          beds_cnv = 1.0
          beds_pre = 1.0
          rn_conv = calendar.monthrange(date.year, date.month)[1]

        # Capex
        if r['Status_id'] == 4:
          convert  = 'CAPEX'
          beds_pot = 1.0
          beds_cnv = 1.0
          beds_cap = 1.0
          rn_conv = calendar.monthrange(date.year, date.month)[1]

        return [beds, beds_cnv, beds_pot, beds_pre, beds_cap, rn_avail, rn_conv, 0, 0, 0]


    # Bed is available (and convertible, and potential)
    beds     = 1.0
    beds_pot = 1.0
    beds_cnv = 1.0
    rn_avail = calendar.monthrange(date.year, date.month)[1]
    rn_conv  = calendar.monthrange(date.year, date.month)[1]

    # Return values
    return [beds, beds_cnv, beds_pot, beds_pre, beds_cap, rn_avail, rn_conv, 0, 0, 0]
  
  # Log
  logger.info('Calculating real beds...')

  # Connection
  con = dbClient.getconn()

  # Existing resources
  sql = '''
  -- All places
  SELECT 
    r.id, r."Code" AS "resource", r."Flat_id" AS "flat", b."Start_date",
    r."Pre_capex_long_term" AS "val_current",
    r."Post_capex" AS "val_residential",
    r."Post_capex" AS "val_cosharing",
    ra."Date_from",
    ra."Date_to",
    CASE
      WHEN r."Billing_type" = 'mes' THEN 'Monthly' 
      WHEN r."Billing_type" = 'quincena' THEN 'Fortnightly' 
      WHEN r."Billing_type" = 'proporcional' THEN 'Daily' 
    END AS "type",
    rft."Code" AS "flat_type",
    rpt."Code" AS "place_type",
    pr."Multiplier" as "multiplier"
  FROM "Resource"."Resource" r 
    INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
    INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
    INNER JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
    LEFT JOIN "Billing"."Pricing_rate" pr on pr.id = r."Rate_id"
    LEFT JOIN "Resource"."Resource_availability" ra ON (r.id = ra."Resource_id" OR r."Room_id" = ra."Resource_id") AND ra."Status_id" = 5 
  WHERE r."Resource_type" = 'plaza'
  
  UNION
  
  -- All rooms without places
  SELECT 
    r.id, r."Code" AS "resource", r."Flat_id" AS "flat", b."Start_date", 
    r."Pre_capex_long_term" AS "val_current",
    r."Post_capex" AS "val_residential",
    r."Post_capex" AS "val_cosharing",
    ra."Date_from",
    ra."Date_to",
    CASE
      WHEN r."Billing_type" = 'mes' THEN 'Monthly' 
      WHEN r."Billing_type" = 'quincena' THEN 'Fortnightly' 
      WHEN r."Billing_type" = 'proporcional' THEN 'Daily' 
    END AS "type",
    rft."Code" AS "flat_type",
    rpt."Code" AS "place_type",
    pr."Multiplier" as "multiplier"
  FROM "Resource"."Resource" r 
    INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
    INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
    INNER JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
    LEFT JOIN "Billing"."Pricing_rate" pr on pr.id = r."Rate_id"
    LEFT JOIN "Resource"."Resource_availability" ra ON (r.id = ra."Resource_id" OR r."Room_id" = ra."Resource_id") AND ra."Status_id" = 5 
  WHERE "Resource_type" = 'habitacion' 
    AND NOT EXISTS (SELECT id FROM "Resource"."Resource" rr WHERE rr."Room_id" = r.id)
  
  UNION
  
  -- All Flats without rooms
  SELECT 
    r.id, r."Code" AS "resource", r.id AS "flat", b."Start_date",
    r."Pre_capex_long_term" AS "val_current",
    r."Post_capex" AS "val_residential",
    r."Post_capex" AS "val_cosharing",
    ra."Date_from",
    ra."Date_to",
    CASE
      WHEN r."Billing_type" = 'mes' THEN 'Monthly' 
      WHEN r."Billing_type" = 'quincena' THEN 'Fortnightly' 
      WHEN r."Billing_type" = 'proporcional' THEN 'Daily' 
    END AS "type",
    rft."Code" AS "flat_type",
    rpt."Code" AS "place_type",
    pr."Multiplier" as "multiplier"
  FROM "Resource"."Resource" r 
    INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
    INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
    LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
    LEFT JOIN "Billing"."Pricing_rate" pr on pr.id = r."Rate_id"
    LEFT JOIN "Resource"."Resource_availability" ra ON (r.id = ra."Resource_id" OR r."Room_id" = ra."Resource_id") AND ra."Status_id" = 5 
  WHERE "Resource_type" = 'piso' 
    AND NOT EXISTS (SELECT id FROM "Resource"."Resource" rr WHERE rr."Flat_id" = r.id)

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
  SELECT ra."Resource_id", ra."Date_from", ra."Date_to", ra."Status_id", ra."Convertible", rs."Not_flat"
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
  df = pd.merge(df_res, df_dates, on='key').drop('key', axis=1)

  # Beds and available nights
  df[['beds', 'beds_cnv', 'beds_pot', 'beds_pre', 'beds_cap', 'available', 'convertible', 'val_current', 'val_residential', 'val_cosharing', ]] = df.apply(count_real, axis=1, result_type='expand')
  df['data_type'] = 'Real'
  logger.info('- Real beds and nights calculated')
  return df


def beds_real(dbClient):

  df = beds_real_calc(dbClient)
  df = df.reset_index(drop=True)
  df['id'] = range(1, 1 + len(df))
  df['id'] = 'BDR' + df['id'].astype(str)
  df.to_csv('csv/beds_real.csv', index=False, sep=',', encoding='utf-8', columns=['id', 'data_type', 'resource', 'date', 'beds', 'beds_cnv', 'beds_pot', 'beds_pre', 'beds_cap', 'available', 'convertible','val_current','val_residential','val_cosharing'])  
  logger.info('- Beds saved')


# ###################################################
# Calculate forecast beds
# ###################################################

def beds_forecast_calc(dbClient):

  # Log
  logger.info('Calculating forecast beds...')

  # Connection
  con = dbClient.getconn()

  # Existing resources
  sql = '''
    SELECT r."Code" as "resource", rf."Date_price" as "date", rf."Beds" as "beds"
    FROM "Resource"."Resource_forecast" rf
    INNER JOIN "Resource"."Resource" r ON r.id = rf."Resource_id"
    WHERE rf."Beds" > 0
    ORDER BY 1, 2
    '''
  try:
    cur = dbClient.execute(con, sql)
    columns = [desc[0] for desc in cur.description]
    df = pd.DataFrame.from_records(cur.fetchall(), columns=columns)
  except Exception as e:
    logger.error(e)
    con.rollback()
    dbClient.putconn(con)
    return None
  finally:
    cur.close()
  logger.info('- Resources retrieved')

  # Beds and available nights
  df['date'] = pd.to_datetime(df['date'], errors='coerce')
  df['available'] = df['beds'] * df['date'].dt.days_in_month.fillna(0).astype(int)
  logger.info('- Forecast beds and nights calculated')
  
  # Empty values
  df['convertible']     = 0 
  df['beds_cnv']        = 0
  df['beds_pot']        = 0
  df['beds_pre']        = 0
  df['beds_cap']        = 0
  df['val_current']     = 0
  df['val_residential'] = 0
  df['val_cosharing']   = 0 
  df['data_type'] = 'Forecast'
  return df


def beds_forecast(dbClient):

  df = beds_forecast_calc(dbClient)
  df = df.reset_index(drop=True)
  df['id'] = range(1, 1 + len(df))
  df['id'] = 'BDF' + df['id'].astype(str)
  df.to_csv('csv/beds_forecast_new.csv', index=False, sep=',', encoding='utf-8', columns=['id', 'data_type', 'resource', 'date', 'beds', 'beds_cnv', 'beds_pot', 'beds_pre', 'beds_cap', 'available', 'convertible','val_current','val_residential','val_cosharing'])  
  logger.info('- Beds saved')