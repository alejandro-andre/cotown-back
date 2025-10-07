# ###################################################
# Imports
# ###################################################

# System includes
import calendar
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Constants
# ###################################################

START_DATE = '2024-01-01'
END_DATE   = '2029-01-01'


# ###################################################
# Calculate real occupancy
# ###################################################

def occupancy_real(dbClient):

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
  logger.info('Calculating real occupancy...')

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

  # Additional columns
  df_books = df_books.reset_index(drop=True)
  df_books['id'] = (df_books.index + 1).astype(str).str.zfill(7)
  df_books['id'] = 'OCR' + df_books['id'].astype(str)
  df_books['data_type'] = 'Real'

  # To CSV
  logger.info('- Occupied and sold nights calculated')
  df_books.to_csv('csv/occupancy_real.csv', index=False, sep=',', encoding='utf-8', columns=['id', 'data_type', 'resource', 'date', 'occupied', 'sold', 'occupied_t', 'sold_t', 'booking', 'stay_length'])
  logger.info('- Occupancy saved')


# ###################################################
# Calculate forecast occupancy
# ###################################################

def occupancy_forecast(dbClient):

  # Log
  logger.info('Calculating forecast occupancy...')

  # Connection
  con = dbClient.getconn()

  # Bookings
  sql = f'''
    SELECT 
      r."Code" as "resource", rf."Date_price" as "date", rf."Beds" as "beds", rf."Occupancy" as "occupancy",
      rf."Pct_long", rf."Pct_medium", rf."Pct_short", 100 - rf."Pct_long" - rf."Pct_medium" - rf."Pct_short" as "Pct_group"
    FROM "Resource"."Resource_forecast" rf
      INNER JOIN "Resource"."Resource" r ON r.id = rf."Resource_id"
    WHERE rf."Beds" > 0
      AND rf."Occupancy" > 0
  '''
  try:
    cur = dbClient.execute(con, sql)
    columns = [desc[0] for desc in cur.description]
    df_occup = pd.DataFrame.from_records(cur.fetchall(), columns=columns)
  except Exception as e:
    logger.error(e)
    con.rollback()
    dbClient.putconn(con)
    return None
  finally:
    cur.close()
  logger.info('- Forecast occupancy retrieved')

  # Stack by stay types
  df_occup = df_occup.rename(
    columns = {
      'Pct_long': 'LONG',
      'Pct_medium': 'MEDIUM',
      'Pct_short': 'SHORT',
      'Pct_group': 'GROUP',
    }
  )
  base_cols = ['resource', 'date', 'beds', 'occupancy']
  df_occup = (
    df_occup[base_cols + ['LONG', 'MEDIUM', 'SHORT', 'GROUP']]
      .set_index(base_cols)
      .stack()
      .reset_index()
  )
  df_occup.columns = ['resource', 'date', 'beds', 'occupancy', 'stay_length', 'pct']

  # Ocuppied and sold nights
  df_occup['date'] = pd.to_datetime(df_occup['date'], errors='coerce')
  df_occup['days_in_month'] = df_occup['date'].dt.days_in_month.fillna(0).astype(int)
  df_occup['occupied'] = df_occup['beds'] * df_occup['occupancy'] * df_occup['pct'] * df_occup['days_in_month'] / 10000
  df_occup['sold'] = df_occup['occupied']
  df_occup = df_occup[df_occup['occupied'] > 0].reset_index(drop=True)

  # Additional columns
  df_occup['occupied_t'] = 0
  df_occup['sold_t']     = 0
  df_occup['booking']    = 0
  df_occup['data_type']  = 'Forecast'

  # Id
  df_occup = df_occup.reset_index(drop=True)
  df_occup['id'] = (df_occup.index + 1).astype(str).str.zfill(6)
  df_occup['id'] = 'OCF' + df_occup['id'].astype(str)


  # To CSV
  logger.info('- Occupied and sold nights calculated')
  df_occup.to_csv('csv/occupancy_forecast.csv', index=False, sep=',', encoding='utf-8', columns=['id', 'data_type', 'resource', 'date', 'occupied', 'sold', 'occupied_t', 'sold_t', 'booking', 'stay_length'])
  logger.info('- Occupancy saved')


# ###################################################
# Calculate stabilised occupancy
# ###################################################

def occupancy_stabilised(dbClient):

  pass