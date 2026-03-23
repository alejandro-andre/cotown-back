# ###################################################
# Imports
# ###################################################

# System includes
import os
import numpy as np
import pandas as pd
from psycopg2.extras import execute_values

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Constants
# ###################################################

BATCH = 2500


# ###################################################
# Execute scripts
# ###################################################

def execute(dbDestination, script):

  # Log
  logger.info('Executing ' + script + '...')
  
  # Get SQL
  file = 'sql/' + script + '.sql'
  fi = open(file, 'r')
  sql = fi.read()
  fi.close()

  # Execute script
  try:
    con = dbDestination.getconn()
    cur = dbDestination.execute(con, sql)
    cur.close()
    dbDestination.putconn(con)
  except Exception as e:
    logger.error(e)
    return False
  return True


# ###################################################
# Get data
# ###################################################

def get_data(dbClient, script):

  # Get CSV
  file = 'csv/' + script + '.csv'
  if os.path.exists(file):
    logger.info('Loading ' + file + '...')
    return pd.read_csv(file)

  # Or get from SQL
  file = 'sql/' + script + '.sql'
  if os.path.exists(file):
    logger.info('Executing SQL...')

    # Load file
    fi = open(file, 'r')
    sql = fi.read()
    fi.close()

    # Execute script
    try:
      con = dbClient.getconn()
      cur = dbClient.execute(con, sql)
      desc = [desc[0] for desc in cur.description]
      data = cur.fetchall()
    except Exception as e:
      logger.error(e)
      con.rollback()
      dbClient.putconn(con)
      return None
    finally:
      cur.close()
      dbClient.putconn(con)
    
    # Dataframe
    df = pd.DataFrame(data, columns=desc)
    return df

  # No data
  return None


# ###################################################
# Insert batch with row-by-row fallback
# ###################################################

def insert_batch(con, sql, batch):
  cur = con.cursor()
  cur.execute("SAVEPOINT sp_batch")
  try:
    execute_values(cur, sql, batch, page_size=len(batch))
    cur.execute("RELEASE SAVEPOINT sp_batch")
    cur.close()
    return len(batch), 0
  except Exception as batch_err:
    cur.execute("ROLLBACK TO SAVEPOINT sp_batch")
    cur.execute("RELEASE SAVEPOINT sp_batch")
    logger.warning(f"Batch of {len(batch)} failed, retrying row by row: {batch_err}")

  ok = 0
  skipped = 0
  for row in batch:
    cur.execute("SAVEPOINT sp_row")
    try:
      execute_values(cur, sql, [row], page_size=1)
      cur.execute("RELEASE SAVEPOINT sp_row")
      ok += 1
    except Exception as row_err:
      cur.execute("ROLLBACK TO SAVEPOINT sp_row")
      cur.execute("RELEASE SAVEPOINT sp_row")
      logger.warning(f"Row skipped: {row_err}")
      skipped += 1

  cur.close()
  return ok, skipped


# ###################################################
# Load entity
# ###################################################

def load(dbOrigin, dbDestination, table, query):

  # Log
  logger.info('Loading ' + query + '...')

  # Get connection (autocommit must be off for SAVEPOINT support)
  con = dbDestination.getconn()
  con.autocommit = False

  # Get data
  data = get_data(dbOrigin, query)
  if data is None or data.empty:
    return

  try:
    # Get table columns
    sql = 'SELECT * FROM gold.' + table + ' LIMIT 0;'
    cur = dbDestination.execute(con, sql)
    columns = [desc[0] for desc in cur.description if desc[0] != 'ts']
    cur.close()

    # Get data columns
    data.columns = [col.lower() for col in data.columns]
    data = data.reindex(columns=columns)
    data = data.astype(object).where(pd.notnull(data), None)

    # Compare columns
    if list(set(columns) - set(data.columns)):
      logger.info(f"Columnas en DESTINO pero no en ORIGEN: {list(set(columns) - set(data.columns))}")
    if list(set(data.columns) - set(columns)):
      logger.info(f"Columnas en ORIGEN pero no en DESTINO: {list(set(data.columns) - set(columns))}")

    # Insert sentence
    fields = ','.join(f'"{c}"' for c in columns)
    sql = f'INSERT INTO gold.{table} ({fields}) VALUES %s'

    # Loop thru all rows in batches
    total = 0
    skipped = 0
    batch = []

    for tpl in data.itertuples(index=False, name=None):
      batch.append(tpl)

      if len(batch) >= BATCH:
        ok, err = insert_batch(con, sql, batch)
        total += ok
        skipped += err
        logger.debug(f'Loaded {ok} record(s), skipped {err}...')
        batch.clear()

    # Insert last block
    if batch:
      ok, err = insert_batch(con, sql, batch)
      total += ok
      skipped += err

    # Commit
    con.commit()
    logger.info(f'Loaded {total} record(s) ok, skipped {skipped}')

  except Exception as error:
    logger.error(error)
    con.rollback()
    logger.info('No data has been loaded\n')

  finally:
    dbDestination.putconn(con)