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

# Custom includes
from library.business.beds import beds_real_calc
from library.business.constants import START_DATE, END_DATE


# ###################################################
# Calculate real occupancy
# ###################################################

def occupancy_real_calc(dbClient):

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
    df = pd.DataFrame.from_records(cur.fetchall(), columns=columns)
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
  df[['occupied', 'occupied_t', 'sold', 'sold_t']] = df.apply(nights, axis=1, result_type='expand')
  df['data_type'] = 'Real'

  # Index
  df = df.reset_index(drop=True)
  df['id'] = (df.index + 1).astype(str).str.zfill(7)
  df['id'] = 'ORE' + df['id'].astype(str)
  logger.info('- Occupied and sold nights calculated')
  return df


def occupancy_real(dbClient):

  df = occupancy_real_calc(dbClient)
  df.to_csv('csv/occupancy_real.csv', index=False, sep=',', encoding='utf-8', columns=['id', 'data_type', 'resource', 'date', 'occupied', 'sold', 'occupied_t', 'sold_t', 'booking', 'stay_length'])
  logger.info('- Occupancy saved')


# ###################################################
# Calculate forecast occupancy
# ###################################################

def occupancy_forecast_calc(dbClient):

  # Log
  logger.info('Calculating forecast occupancy...')

  # Connection
  con = dbClient.getconn()

  # Forecast
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
    df = pd.DataFrame.from_records(cur.fetchall(), columns=columns)
  except Exception as e:
    logger.error(e)
    con.rollback()
    dbClient.putconn(con)
    return None
  finally:
    cur.close()
  logger.info('- Forecast data retrieved')

  # Stack by stay types
  df = df.rename(
    columns = {
      'Pct_long': 'LONG',
      'Pct_medium': 'MEDIUM',
      'Pct_short': 'SHORT',
      'Pct_group': 'GROUP',
    }
  )
  base_cols = ['resource', 'date', 'beds', 'occupancy']
  df = (
    df[base_cols + ['LONG', 'MEDIUM', 'SHORT', 'GROUP']]
      .set_index(base_cols)
      .stack()
      .reset_index()
  )
  df.columns = ['resource', 'date', 'beds', 'occupancy', 'stay_length', 'pct']

  # Ocuppied and sold nights
  df['date'] = pd.to_datetime(df['date'], errors='coerce')
  df['days_in_month'] = df['date'].dt.days_in_month.fillna(0).astype(int)
  df['occupied'] = df['beds'] * df['occupancy'] * df['pct'] * df['days_in_month'] / 10000
  df['sold'] = df['occupied']
  df = df[df['occupied'] > 0].reset_index(drop=True)

  # Additional columns
  df['occupied_t'] = 0
  df['sold_t']     = 0
  df['booking']    = 0
  df['data_type']  = 'Forecast'

  # Index
  df = df.reset_index(drop=True)
  df['id'] = (df.index + 1).astype(str).str.zfill(6)
  df['id'] = 'OFO' + df['id'].astype(str)
  logger.info('- Occupied and sold nights calculated')
  return df


def occupancy_forecast(dbClient):

  df = occupancy_forecast_calc(dbClient)
  df.to_csv('csv/occupancy_forecast.csv', index=False, sep=',', encoding='utf-8', columns=['id', 'data_type', 'resource', 'date', 'occupied', 'sold', 'occupied_t', 'sold_t', 'booking', 'stay_length'])
  logger.info('- Occupancy saved')


# ###################################################
# Calculate stabilised occupancy
# ###################################################

def occupancy_stabilised_calc(dbClient):

  # Log
  logger.info('Calculating stabilised occupancy...')

  # Connection
  con = dbClient.getconn()

  # Stabilised hypotesis
  sql = f'''
    SELECT 
      r."Code" as "flat", rs."Date_price" as "month", rs."Occupancy" as "occupancy", 
      rs."Pct_long" as "pct_long", rs."Pct_medium" as "pct_medium", rs."Pct_short" as "pct_short"
    FROM "Resource"."Resource_stabilised" rs
      INNER JOIN "Resource"."Resource" r ON r.id = rs."Resource_id"
  '''
  try:
    cur = dbClient.execute(con, sql)
    columns = [desc[0] for desc in cur.description]
    df_occ = pd.DataFrame.from_records(cur.fetchall(), columns=columns)
  except Exception as e:
    logger.error(e)
    con.rollback()
    dbClient.putconn(con)
    return None
  finally:
    cur.close()
  df_occ['pct_group'] = 100 - df_occ['pct_long'] - df_occ['pct_medium'] - df_occ['pct_short']
  logger.info('- Stabilised data retrieved')
 
  # Calculate beds
  df_beds = beds_real_calc(dbClient)

  # Merge by resource and month
  df_beds['flat'] = df_beds['resource'].str.slice(0, 12)
  df_beds['date'] = pd.to_datetime(df_beds['date'])
  df_beds['month'] = df_beds['date'].dt.month
  df_beds['days_in_month'] = df_beds['date'].dt.days_in_month.fillna(0).astype(int)
  df_sta = df_beds.merge(
    df_occ,
    left_on=['flat', 'month'],
    right_on=['flat', 'month'],
    how='left'
  )

  # Duplicate DF
  df_stc = df_sta.copy()   

  # Occupied and sold nights
  df_sta['occupied'] = df_sta['beds'].astype(float) * df_sta['occupancy'].astype(float) * df_sta['days_in_month'] / 100
  df_sta['sold'] = df_sta['occupied']
  df_sta = df_sta[df_sta['occupied'] > 0].reset_index(drop=True)
  df_stc['occupied'] = df_stc['beds_cnv'].astype(float) * df_stc['occupancy'].astype(float) * df_stc['days_in_month'] / 100
  df_stc['sold'] = df_stc['occupied']
  df_stc = df_stc[df_stc['occupied'] > 0].reset_index(drop=True)

  # Additional columns
  df_sta['occupied_t']  = 0
  df_sta['sold_t']      = 0
  df_sta['booking']     = 0
  df_sta['stay_length'] = ''
  df_sta['data_type']   = 'Stabilised Available'
  df_stc['occupied_t']  = 0
  df_stc['sold_t']      = 0
  df_stc['booking']     = 0
  df_stc['stay_length'] = ''
  df_stc['data_type']   = 'Stabilised Convertible'

  # Indexes
  df_sta = df_sta.reset_index(drop=True)
  df_sta['id'] = (df_sta.index + 1).astype(str).str.zfill(6)
  df_sta['id'] = 'OSA' + df_sta['id'].astype(str)
  df_stc = df_stc.reset_index(drop=True)
  df_stc['id'] = (df_stc.index + 1).astype(str).str.zfill(6)
  df_stc['id'] = 'OSC' + df_stc['id'].astype(str)
  logger.info('- Occupied and sold nights calculated')
  return pd.concat([df_sta, df_stc], ignore_index=True)

def occupancy_stabilised(dbClient):

  df = occupancy_stabilised_calc(dbClient)
  df.to_csv('csv/occupancy_stabilised.csv', index=False, sep=',', encoding='utf-8', columns=['id', 'data_type', 'resource', 'date', 'occupied', 'sold', 'occupied_t', 'sold_t', 'booking', 'stay_length'])
  logger.info('- Occupancy saved')