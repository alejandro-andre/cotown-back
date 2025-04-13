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

  def count(row):
    # Date
    date = row['date']

    # Building started?
    if date < row['Start_date']:
      return 'OUT'

    # All flat non availability rows
    availability = df_avail[df_avail['id'] == row['flat']]
    for _, r in availability.iterrows():
      if r['Date_from'] <= date <= r['Date_to']:
        return r['Type']

    # Default
    return 'COSHARING'
  
  
  # Log
  logger.info('Calculating resources history...')

  # Connection
  con = dbClient.getconn()

  # Existing (all) resources
  sql = '''
    SELECT
      r."Code" as "resource",
      COALESCE(r."Area", 0) as "area",
      CASE 
        WHEN r."Resource_type" = 'piso' THEN r.id
        ELSE r."Flat_id"
      END AS "flat",
      CASE 
        WHEN r."Resource_type" = 'plaza' THEN 1
        WHEN r."Resource_type" = 'habitacion' THEN (
          SELECT GREATEST(1, COUNT(*))
          FROM "Resource"."Resource" rr
          WHERE rr."Room_id" = r.id
        )
        ELSE (
          SELECT COUNT("Flat_id") - COUNT("Room_id") / 2
          FROM "Resource"."Resource" rr
          WHERE rr."Flat_id" = r.id
        )
      END AS "beds",
      CASE 
        WHEN r."Resource_type" = 'plaza' THEN 0
        WHEN r."Resource_type" = 'piso' THEN (
          SELECT COUNT(*)
          FROM "Resource"."Resource" rr
          WHERE rr."Flat_id" = r.id
          AND rr."Resource_type" = 'habitacion'
        )
        ELSE 1
      END AS "rooms",
      b."Start_date"
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
  logger.info('- Unavailabilities retrieved')

  # Dates
  df_dates = pd.DataFrame({'date': [date.date() for date in pd.date_range(start=START_DATE, end=END_DATE, freq='MS')]})

  # Resources x dates Cross table
  df_dates['key'] = 1
  df_res['key'] = 1
  df_history = pd.merge(df_res, df_dates, on='key').drop('key', axis=1)

  # Calculate
  df_history['status'] = df_history.apply(count, axis=1, result_type='expand')
  logger.info('- History calculated')

  # To CSV
  df_history['id'] = range(1, 1 + len(df_history))
  df_history['data_type'] = 'Real'
  df_history['val_current'] = 0
  df_history['val_residential'] = 0
  df_history['val_cosharing'] = 0
  df_history.to_csv('csv/history_real.csv', index=False, sep=',', encoding='utf-8', columns=['id', 'data_type', 'resource', 'date', 'status', 'area', 'rooms', 'beds', 'val_current','val_residential','val_cosharing'])  
  logger.info('- History saved')