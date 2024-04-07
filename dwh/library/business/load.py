# ###################################################
# Imports
# ###################################################

# System includes
import os
import pandas as pd
import json

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Execute scripts
# ###################################################

def execute(dbDestination, script):

  # Get script
  file = 'sql/' + script + '.sql'
  if not os.path.exists(file):
    return False
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

  # Get script
  file = 'sql/' + script + '.sql'
  if not os.path.exists(file):
    return None
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


# ###################################################
# Load entity
# ###################################################

def load(dbOrigin, dbDestination, table):

  # Log
  logger.info('Loading ' + table + 's...')

  # Get data
  data = get_data(dbOrigin, table)
  if data is None or data.empty:
    return

  # Get connection
  con = dbDestination.getconn()

  # Get table columns
  sql = 'SELECT * FROM gold.' + table + ' LIMIT 0;'
  cur = dbDestination.execute(con, sql)
  columns = [desc[0] for desc in cur.description]
  cur.close()

  # Get data columns
  data.columns = [col.lower() for col in data.columns]

  # Compare columns
  if list(set(columns) - set(data.columns)):
    logger.info(f"Columnas en DESTINO pero no en ORIGEN: {list(set(columns) - set(data.columns))}")
  if list(set(data.columns) - set(columns)):
    logger.info(f"Columnas en ORIGEN pero no en DESTINO: {list(set(data.columns) - set(columns))}")

  # Insert sentence
  fields = list(map(lambda key: '"' + key + '"', columns))
  update = list(map(lambda key: '"' + key + '"=EXCLUDED."' + key + '"', columns))
  markers = ['%s'] * len(columns)
  sql = 'INSERT INTO gold.' + table + ' ({}) VALUES ({}) ON CONFLICT (id) DO UPDATE SET {}'.format(','.join(fields), ','.join(markers), ','.join(update))

  try:
    # Loop thru all rows
    records = []
    for _, row in data.iterrows():
      # Append record
      record = {col.lower(): (None if pd.isna(row[col]) else row[col]) for col in columns}
      records.append(list(record.values()))

      # Insert block
      if len(records) == 500:
        cur = dbDestination.executemany(con, sql, records)
        cur.close()
        logger.info('Loaded ' + str(len(records)) + ' record(s)...')
        records = []
          
    # Insert last block
    if len(records):
      cur = dbDestination.executemany(con, sql, records)
      cur.close()

  except Exception as error:
    logger.error(error)
    logger.info('No data has been loaded\n')
    con.rollback()
    dbDestination.putconn(con)
    return

  # Commit
  logger.info('Loaded ' + str(len(data)) + ' record(s) ok')
  con.commit()
  dbDestination.putconn(con)