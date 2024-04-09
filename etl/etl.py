# ###################################################
# DWH Scripts
# ---------------------------------------------------
# Create tables at DWH
# ###################################################

# ###################################################
# Imports
# ###################################################

# System includes
import os

# Cotown includes
from library.services.dbclient import DBClient
from library.services.config import settings
from library.business.load import load, execute

# Logging
import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger('COTOWN')

# ###################################################
# Connect to BD
# ###################################################

def connect():

# ---------------------------------------------------
# Open origin DB
# ---------------------------------------------------

  dbOrigin = DBClient(
    host=settings.DBHOST,
    dbname=settings.DBNAME,
    user=settings.DBUSER,
    password=settings.DBPASS,
    sshuser=settings.SSHUSER,
    sshpassword=settings.get('SSHPASS', None),
    sshprivatekey=settings.get('SSHPKEY', None),
    readonly=True
  )
  dbOrigin.connect()


# ---------------------------------------------------
# Open destination DB
# ---------------------------------------------------

  dbDestination = DBClient(
    host=settings.DWDBHOST,
    dbname=settings.DWDBNAME,
    user=settings.DWDBUSER,
    password=settings.DWDBPASS,
    sshuser=settings.DWSSHUSER,
    sshpassword=settings.get('DWSSHPASS', None),
    sshprivatekey=settings.get('DWSSHPKEY', None)
  )
  dbDestination.connect()

  return dbOrigin, dbDestination

  '''
  columnas = cur.description
  for col in columnas:
      cur.execute("SELECT typname FROM pg_type WHERE oid = %s;", (col.type_code,))
      type_name = cur.fetchone()
      print(f'{col.name}, {col.type_code}, {type_name[0]}')

  '''

# ###################################################
# Startup
# ###################################################

if __name__ == '__main__':

  # Logging

  logger.setLevel(settings.LOGLEVEL)
  formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(module)s] [%(funcName)s/%(lineno)3d] [%(levelname)s] %(message)s')
  console_handler = logging.StreamHandler()
  console_handler.setLevel(settings.LOGLEVEL)
  console_handler.setFormatter(formatter)
  file_handler = RotatingFileHandler('log/etl.log', maxBytes=1000000, backupCount=5)
  file_handler.setLevel(settings.LOGLEVEL)
  file_handler.setFormatter(formatter)
  logger.addHandler(console_handler)
  logger.addHandler(file_handler)
  logger.info('Started')

  # Connect
  dbOrigin, dbDestination = connect()

  # Init destination
  execute(dbDestination, '_init')

  # Load tables
  load(dbOrigin, dbDestination, 'owner', 'owner')
  load(dbOrigin, dbDestination, 'location', 'location')
  load(dbOrigin, dbDestination, 'product', 'product')
  load(dbOrigin, dbDestination, 'resource', 'resource')
  load(dbOrigin, dbDestination, 'income', 'income_b2b_real')
  load(dbOrigin, dbDestination, 'income', 'income_b2b_otb')
  load(dbOrigin, dbDestination, 'income', 'income_b2c_real')
  load(dbOrigin, dbDestination, 'income', 'income_b2c_otb')
  load(dbOrigin, dbDestination, 'income', 'income_forecast')

  # Disconnect
  dbDestination.disconnect()
  dbOrigin.disconnect()

