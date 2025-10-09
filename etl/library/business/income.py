# ###################################################
# Imports
# ###################################################

# System includes
import numpy as np
import pandas as pd

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Custom includes
from library.business.beds import beds_real_calc
from library.business.constants import START_DATE, END_DATE


# ###################################################
# Calculate forecast income
# ###################################################

def income_forecast_calc(dbClient):

  # Log
  logger.info('Calculating forecast income...')

  # Connection
  con = dbClient.getconn()

  # Bookings
  sql = f'''
    SELECT 
      r."Code" as "resource", rf."Date_price" as "date", rf."Beds" as "beds", rf."Occupancy" as "occupancy",
      rf."Pct_long", rf."Pct_medium", rf."Pct_short", 100 - rf."Pct_long" - rf."Pct_medium" - rf."Pct_short" as "Pct_group",
      rf."Rent_short", rf."Rent_medium", rf."Rent_long", rf."Rent_group",
      rf."Discount", rf."Services", rf."Final_cleaning", rf."Booking_fee", rf."Reinvoices",
      rf."Management_fee", b."Building_type_id" as "type"
    FROM "Resource"."Resource_forecast" rf
      INNER JOIN "Resource"."Resource" r ON r.id = rf."Resource_id"
      INNER JOIN "Building"."Building" b ON b.id = r."Building_id" 
    --WHERE rf."Beds" > 0 AND rf."Occupancy" > 0
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

  # Calculate amounts
  df['date'] = pd.to_datetime(df['date'], errors='coerce')
  df['days_in_month']  = df['date'].dt.days_in_month.fillna(0).astype(int)
  df['Rent_short']     = df['beds'].astype(float) * df['occupancy'].astype(float) * df['Rent_short'].astype(float)  * df['Pct_short'].astype(float)  * (100.0 - df['Discount'].astype(float)) / 1000000
  df['Rent_medium']    = df['beds'].astype(float) * df['occupancy'].astype(float) * df['Rent_medium'].astype(float) * df['Pct_medium'].astype(float) * (100.0 - df['Discount'].astype(float)) / 1000000
  df['Rent_long']      = df['beds'].astype(float) * df['occupancy'].astype(float) * df['Rent_long'].astype(float)   * df['Pct_long'].astype(float)   * (100.0 - df['Discount'].astype(float)) / 1000000
  df['Rent_group']     = df['beds'].astype(float) * df['occupancy'].astype(float) * df['Rent_group'].astype(float)  * df['Pct_group'].astype(float)  * (100.0 - df['Discount'].astype(float)) / 1000000
  df['Management_fee'] = np.where(
    df['type'] == 3, 
    df['Management_fee'].astype(float) * (df['Rent_long'] + df['Rent_medium'] + df['Rent_short'] + df['Rent_group']) / 110.0,
    df['Management_fee'].astype(float) * (df['Rent_long'] + df['Rent_medium'] + df['Rent_short'] + df['Rent_group']) / 100.0
  )
  # Stack by stay types
  df = df.rename(
    columns = {
      'Rent_long': 'LONG',
      'Rent_medium': 'MEDIUM',
      'Rent_short': 'SHORT',
      'Rent_group': 'GROUP',
      'Services': 'Periodic cleaning service',
      'Final_cleaning': 'Check-out cleaning services',
      'Booking_fee': 'Membership fee',
      'Reinvoices': 'Others',
      'Management_fee': 'Management fee',
    }
  )
  base_cols = ['resource', 'date', 'type']
  df = (
    df[base_cols + ['LONG', 'MEDIUM', 'SHORT', 'GROUP', 'Periodic cleaning service', 'Check-out cleaning services', 'Membership fee', 'Others', 'Management fee']]
      .set_index(base_cols)
      .stack()
      .reset_index()
  )
  df.columns = ['resource', 'date', 'type', 'stay_length', 'amount']

  # Amounts
  df = df[df['amount'].notna() & (df['amount'] != 0)]
  df['rate']   = df['amount']
  df['price']  = df['amount']
  
  # Products and stay length
  cond = df['stay_length'].isin(['LONG', 'MEDIUM', 'SHORT', 'GROUP'])
  df['product']     = np.where(cond, 'Monthly rent', df['stay_length'])
  df['stay_length'] = np.where(cond, df['stay_length'], '')

  # Additional columns
  df['data_type']     = 'Forecast'
  df['booking']       = '-'
  df['doc_type']      = '-'
  df['doc_id']        = '-'
  df['provider']      = None
  df['customer']      = None
  df['discount_type'] = None

  # Index
  df = df.reset_index(drop=True)
  df['id'] = (df.index + 1).astype(str).str.zfill(6)
  df['id'] = 'IFO' + df['id'].astype(str)
  logger.info('- Income calculated')
  return df


def income_forecast(dbClient):

  df = income_forecast_calc(dbClient)
  df.to_csv('csv/income_forecast.csv', index=False, sep=',', encoding='utf-8', columns=['id', 'doc_id', 'doc_type', 'booking', 'date', 'provider', 'customer', 'resource', 'product', 'amount', 'rate', 'price', 'data_type', 'stay_length', 'discount_type'])
  logger.info('- Income saved')


# ###################################################
# Calculate stabilised income
# ###################################################

def income_stabilised_calc(dbClient):

  # Log
  logger.info('Calculating stabilised income...')

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

  # Prices
  sql = f'''
    SELECT 
      pd."Year" AS "year", b."Code" AS "building", rft."Code" AS "flat_type", rpt."Code" AS "place_type", 
      pd."Rent_long" AS "long", pd."Rent_medium" AS "medium", pd."Rent_short" AS "short", COALESCE(pd."Rent_group", 0) AS "group"
    FROM "Billing"."Pricing_detail" pd
      INNER JOIN "Building"."Building" b ON b.id = pd."Building_id"
      INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = pd."Flat_type_id"
      INNER JOIN "Resource"."Resource_place_type" rpt ON rpt.id = pd."Place_type_id"
  '''
  try:
    cur = dbClient.execute(con, sql)
    columns = [desc[0] for desc in cur.description]
    df_price = pd.DataFrame.from_records(cur.fetchall(), columns=columns)
  except Exception as e:
    logger.error(e)
    con.rollback()
    dbClient.putconn(con)
    return None
  finally:
    cur.close()
  logger.info('- Prices retrieved')
  
  # Calculate beds
  df_beds = beds_real_calc(dbClient)

  # Prepare merges
  df_beds['date'] = pd.to_datetime(df_beds['date'])
  df_beds['year'] = np.where(df_beds['date'].dt.month >= 9, df_beds['date'].dt.year + 1, df_beds['date'].dt.year)
  df_beds['month'] = df_beds['date'].dt.month
  df_beds['building'] = df_beds['resource'].str.slice(0, 6)
  df_beds['flat'] = df_beds['resource'].str.slice(0, 12)

  # Merge occ by resource and month
  df_ina = df_beds.merge(
    df_occ,
    left_on=['flat', 'month'],
    right_on=['flat', 'month'],
    how='left'
  )

  # Merge rates by flat and month
  df_ina = df_ina.merge(
    df_price,
    left_on=['building', 'year', 'flat_type', 'place_type'],
    right_on=['building', 'year', 'flat_type', 'place_type'],
    how='left'
  )

  # Calcs
  df_ina.fillna(0)
  df_ina['product'] = 'Monthly rent'
  df_ina['stay_length'] = ''

  # Additional columns
  df_ina['doc_id']        = '-'
  df_ina['doc_type']      = '-'
  df_ina['booking']       = '-'
  df_ina['provider']      = ''
  df_ina['customer']      = ''
  df_ina['price']         = ''
  df_ina['discount_type'] = ''

  # Duplicate DF
  df_inc = df_ina.copy()   

  # Amounts
  df_ina['data_type'] = 'Stabilised Available'
  df_ina['amount'] = df_ina['beds'].astype(float) * df_ina['occupancy'].astype(float) * (df_ina['pct_long'] * df_ina['long'] + df_ina['pct_medium'] * df_ina['medium'] + df_ina['pct_short'] * df_ina['short'] + df_ina['pct_group'] * df_ina['group']).astype(float) / 10000
  df_ina['rate'] = df_ina['amount']
  df_ina = df_ina[df_ina['amount'].notna() & (df_ina['amount'] != 0)]
  df_inc['data_type'] = 'Stabilised Convertible'
  df_inc['amount'] = df_inc['beds_cnv'].astype(float) * df_inc['occupancy'].astype(float) * (df_inc['pct_long'] * df_inc['long'] + df_inc['pct_medium'] * df_inc['medium'] + df_inc['pct_short'] * df_inc['short'] + df_inc['pct_group'] * df_inc['group']).astype(float) / 10000
  df_inc['rate'] = df_inc['amount']
  df_inc = df_inc[df_inc['amount'].notna() & (df_inc['amount'] != 0)]

  # Indexes
  df_ina = df_ina.reset_index(drop=True)
  df_ina['id'] = (df_ina.index + 1).astype(str).str.zfill(6)
  df_ina['id'] = 'ISA' + df_ina['id'].astype(str)
  df_inc = df_inc.reset_index(drop=True)
  df_inc['id'] = (df_inc.index + 1).astype(str).str.zfill(6)
  df_inc['id'] = 'ISC' + df_inc['id'].astype(str)
  logger.info('- Income calculated')
  return pd.concat([df_ina, df_inc], ignore_index=True)


def income_stabilised(dbClient):

  df = income_stabilised_calc(dbClient)
  df.to_csv('csv/income_stabilised.csv', index=False, sep=',', encoding='utf-8', columns=['id', 'doc_id', 'doc_type', 'booking', 'date', 'provider', 'customer', 'resource', 'product', 'amount', 'rate', 'price', 'data_type', 'stay_length', 'discount_type'])
  logger.info('- Income saved')