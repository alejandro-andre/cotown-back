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
# Calculate resource history
# ###################################################

def history(dbClient):

  # Get valuation
  def valuate(row, val_grouped):
    # Data
    status = row['status']
    resource = row['resource']
    date = row['date']
    
    # Not valuated
    if resource not in val_grouped.groups:
      return pd.Series([0, 0, 0])
    
    # Get recent valuation or oldest one
    values = val_grouped.get_group(resource)
    valid_values = values[values['Valuation_date'] <= date]
    if not valid_values.empty:
      best = valid_values.iloc[-1]
    else:
      best = values.iloc[0]

    # Current value
    current = best['Pre_capex_long_term'] or 0
    if status == 'COSHARING':
      current = best['Post_capex'] or 0
    elif status in ('PRECAPEX', 'CAPEX', ):
      current = best['Pre_capex_vacant'] or 0

    # Return
    return pd.Series([current, best['Post_capex_residential'] or 0, best['Post_capex'] or 0])


  # Get status
  def status(row, avail_grouped):

    # Status type
    def default_type(resource_type):
      if resource_type == 'local':
        return 'RETAIL'
      elif resource_type == 'parking':
        return 'PARKING'
      elif resource_type == 'trastero':
        return 'STORAGE'
      return 'COSHARING'
    
    # Data
    date = row['date']
    flat_id = row['flat']

    # Building not active
    if date < row['Start_date']:
      return 'OUT'

    # No unavailabilities
    if flat_id not in avail_grouped.groups:
      return default_type(row['Resource_type'])

    # Search availability for that resource and date
    availability = avail_grouped.get_group(flat_id)
    for _, r in availability.iterrows():
      if r['Date_from'] <= date <= r['Date_to']:
        return r['Type']

    # Default
    return default_type(row['Resource_type'])


  # Connection
  logger.info('Calculating resources history...')
  con = dbClient.getconn()

  # Existing (all) resources
  sql = '''
    SELECT
      r."Code" as "resource",
      b."Start_date",
      r."Resource_type",
      CASE 
        WHEN r."Resource_type" = 'piso' THEN r.id
        ELSE r."Flat_id"
      END AS "flat",
      CASE 
        WHEN r."Resource_type" = 'piso' THEN COALESCE(r."Area", 0)
        ELSE 0
      END AS "area",
      CASE 
        WHEN r."Resource_type" = 'plaza' THEN 1
        WHEN r."Resource_type" = 'habitacion' THEN (
          SELECT CASE WHEN COUNT(*) > 0 THEN 0 ELSE 1 END
          FROM "Resource"."Resource" rr
          WHERE rr."Room_id" = r.id    )
        ELSE 0
      END AS "beds",
      CASE
        WHEN r."Resource_type" = 'habitacion' THEN 1
        ELSE 0
      END AS "rooms",
      CASE
        WHEN r."Resource_type" IN ('habitacion', 'plaza') THEN 0
        ELSE 1
      END AS "units"
    FROM "Resource"."Resource" r
      INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
    ORDER BY 1
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

  # Valuations
  sql = '''
    SELECT 
      r."Code" as "resource", 
      rv."Valuation_date",
      rv."Pre_capex_long_term",
      rv."Pre_capex_vacant",
      rv."Post_capex_residential",
      rv."Post_capex"
    FROM "Resource"."Resource_value" rv 
      INNER JOIN "Resource"."Resource" r on r.id = rv."Resource_id"
  '''
  try:
    cur = dbClient.execute(con, sql)
    columns = [desc[0] for desc in cur.description]
    df_values = pd.DataFrame.from_records(cur.fetchall(), columns=columns)
  except Exception as e:
    logger.error(e)
    con.rollback()
    dbClient.putconn(con)
    return None
  finally:
    cur.close()
  df_val_by_resource = df_values.groupby('resource')
  logger.info('- Valuations retrieved')

  # Availability each month
  sql = '''
    SELECT
      r.id, 
      ra."Date_from",
      ra."Date_to",
      CASE
        WHEN ra."Status_id" = 2 THEN 
          CASE
            WHEN bo.id IS NULL THEN 'FTC'
            WHEN bo."Date_to" IS NULL AND bo."Date_estimated" IS NOT NULL THEN 'LTC'
            WHEN bo."Date_to" IS NOT NULL THEN 'FTC'
            ELSE 'LTNC'
          END
        WHEN ra."Status_id" = 3 THEN 'PRECAPEX'
        WHEN ra."Status_id" = 4 THEN 'CAPEX'
        ELSE UPPER(rs."Name")
      END AS "Type" 
    FROM "Resource"."Resource" r
      LEFT JOIN "Resource"."Resource_availability" ra ON r.id = ra."Resource_id" 
      LEFT JOIN "Resource"."Resource_status" rs ON rs.id = ra."Status_id"
      LEFT JOIN "Booking"."Booking_other" bo ON r.id = bo."Resource_id"
    WHERE r."Resource_type" NOT IN ('habitacion', 'plaza')
      AND rs."Available" = FALSE
    ORDER BY 1, 2
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
  df_avail_by_flat = df_avail.groupby('id')
  logger.info('- Unavailabilities retrieved')

  # Dates
  df_dates = pd.DataFrame({'date': [date.date() for date in pd.date_range(start=START_DATE, end=END_DATE, freq='MS')]})

  # Resources x dates Cross table
  df_dates['key'] = 1
  df_res['key'] = 1
  df_history = pd.merge(df_res, df_dates, on='key').drop('key', axis=1)

  # Status
  df_history['status'] = df_history.apply(lambda row: status(row, df_avail_by_flat), axis=1)
  logger.info('- Status calculated')

  # Valuation
  df_history[['val_current', 'val_residential', 'val_cosharing']] = df_history.apply(lambda row: valuate(row, df_val_by_resource), axis=1)
  logger.info('- Valuations calculated')

  # To CSV
  df_history['id'] = range(1, 1 + len(df_history))
  df_history['data_type'] = 'Real'
  df_history.to_csv('csv/history_real.csv', index=False, sep=',', encoding='utf-8', columns=['id', 'data_type', 'resource', 'date', 'status', 'area', 'units', 'rooms', 'beds', 'val_current','val_residential','val_cosharing'])  
  logger.info('- History saved')