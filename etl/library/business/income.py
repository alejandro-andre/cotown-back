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
  logger.info('- Stabilised occupancy retrieved')

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
  df_beds['days_in_month'] = df_beds['date'].dt.days_in_month.fillna(0).astype(int)
  df_beds['building'] = df_beds['resource'].str.slice(0, 6)
  df_beds['flat'] = df_beds['resource'].str.slice(0, 12)

  # Merge occ by resource and month
  df = df_beds.merge(
    df_occ,
    left_on=['flat', 'month'],
    right_on=['flat', 'month'],
    how='left'
  )

  # Merge rates by flat and month
  df = df.merge(
    df_price,
    left_on=['building', 'year', 'flat_type', 'place_type'],
    right_on=['building', 'year', 'flat_type', 'place_type'],
    how='left'
  )

  # Calcs
  df.fillna(0)
  df['product'] = 'Monthly rent'
  df['stay_length'] = ''

  # Amounts
  df['amount'] = df['beds'].astype(float) * df['days_in_month'].astype(float) * df['occupancy'].astype(float) * (df['pct_long'] * df['long'] + df['pct_medium'] * df['medium'] + df['pct_short'] * df['short'] + df['pct_group'] * df['group']).astype(float) / 10000
  df['rate'] = df['amount']
  df = df[df['amount'].notna() & (df['amount'] != 0)]
                  
  # Additional columns
  df['data_type']     = 'Stabilised Available'
  df['doc_id']        = '-'
  df['doc_type']      = '-'
  df['booking']       = '-'
  df['provider']      = ''
  df['customer']      = ''
  df['price']         = ''
  df['discount_type'] = ''
  logger.info('- Income calculated')
  return(df)


def income_stabilised(dbClient):

  df = income_stabilised_calc(dbClient)
  df = df.reset_index(drop=True)
  df['id'] = (df.index + 1).astype(str).str.zfill(6)
  df['id'] = 'INA' + df['id'].astype(str)
  df.to_csv('csv/income_stabilised.csv', index=False, sep=',', encoding='utf-8', columns=['id', 'doc_id', 'doc_type', 'booking', 'date', 'provider', 'customer', 'resource', 'product', 'amount', 'rate', 'price', 'data_type', 'stay_length', 'discount_type'])
  logger.info('- Income saved')