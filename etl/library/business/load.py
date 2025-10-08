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
# Load entity
# ###################################################

def load(dbOrigin, dbDestination, table, query):

  # Log
  logger.info('Loading ' + query + '...')

  # Get connection
  con = dbDestination.getconn()

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

    # Cursor
    total = 0
    cur = con.cursor()

    # Generate tuples
    def row_gen():
      for tpl in data.itertuples(index=False, name=None):
        yield tpl
      
    # Loop thru all rows
    batch = []
    for row in row_gen():
      batch.append(row)

      # Insert block
      if len(batch) >= BATCH:
        execute_values(cur, sql, batch, page_size=BATCH)
        total += len(batch)
        logger.debug('Loaded ' + str(len(batch)) + ' record(s)...')
        batch.clear()
          
    # Insert last block
    if batch:
      execute_values(cur, sql, batch, page_size=BATCH)
      total += len(batch)

    # Commit
    con.commit()
    logger.info('Loaded ' + str(total) + ' record(s) ok')

  except Exception as error:
    logger.error(error)
    con.rollback()
    logger.info('No data has been loaded\n')

  finally:
    dbDestination.putconn(con)