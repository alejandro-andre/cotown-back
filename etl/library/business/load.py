# ###################################################
# Imports
# ###################################################

# System includes
import os
import pandas as pd

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Constants
# ###################################################

BATCH = 1000


# ###################################################
# Execute scripts
# ###################################################

def execute(dbDestination, script):

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
    return pd.read_csv(file)

  # Or get from SQL
  file = 'sql/' + script + '.sql'
  if os.path.exists(file):

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

  # Get data
  data = get_data(dbOrigin, query)
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
  markers = ['%s'] * len(columns)
  fields = list(map(lambda key: '"' + key + '"', columns))
  #update = list(map(lambda key: '"' + key + '"=EXCLUDED."' + key + '"', columns))
  #sql = 'INSERT INTO gold.' + table + ' ({}) VALUES ({}) ON CONFLICT (id) DO UPDATE SET {}'.format(','.join(fields), ','.join(markers), ','.join(update))
  sql = 'INSERT INTO gold.' + table + ' ({}) VALUES ({})'.format(','.join(fields), ','.join(markers))

  try:
    # Loop thru all rows
    records = []
    for _, row in data.iterrows():
      # Append record
      record = {col.lower(): (None if pd.isna(row[col]) else row[col]) for col in columns}
      records.append(list(record.values()))

      # Insert block
      if len(records) >= BATCH:
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