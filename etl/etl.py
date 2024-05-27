# ###################################################
# DWH Scripts
# ---------------------------------------------------
# Create tables at DWH
# ###################################################

# ###################################################
# Imports
# ###################################################

# Cotown includes
from library.services.dbclient import DBClient
from library.services.config import settings
from library.business.load import load, execute
from library.business.occupancy import occupancy
from library.business.forecast import forecast

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
    port=settings.get('DBPORT', 5432),
    dbname=settings.DBNAME,
    user=settings.DBUSER,
    password=settings.DBPASS,
    sshuser=settings.get('SSHUSER', None),
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
    port=settings.get('DWDBPORT', 5432),
    dbname=settings.DWDBNAME,
    user=settings.DWDBUSER,
    password=settings.DWDBPASS,
    sshuser=settings.get('DWSSHUSER', None),
    sshpassword=settings.get('DWSSHPASS', None),
    sshprivatekey=settings.get('DWSSHPKEY', None)
  )
  dbDestination.connect()

  return dbOrigin, dbDestination


# ###################################################
# Main
# ###################################################

def main():

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
  try:
    dbOrigin, dbDestination = connect()
  except Exception as e:
    logger.error(e)
    return

  # Process
  try:
    # Init destination
    execute(dbDestination, '_init')

    load(dbOrigin, dbDestination, 'income', 'income_b2b_real')
    load(dbOrigin, dbDestination, 'income', 'income_b2b_otb')
    load(dbOrigin, dbDestination, 'income', 'income_b2c_real')
    load(dbOrigin, dbDestination, 'income', 'income_b2c_otb')
    
    # Load dimensions
    load(dbOrigin, dbDestination, 'owner', 'owner')
    load(dbOrigin, dbDestination, 'flat_type', 'flat_type')
    load(dbOrigin, dbDestination, 'place_type', 'place_type')
    load(dbOrigin, dbDestination, 'location', 'location')
    load(dbOrigin, dbDestination, 'product', 'product')
    load(dbOrigin, dbDestination, 'resource', 'resource')

    # Calc forecast
    forecast()

    # Calc availability
    occupancy(dbOrigin)

    # Load facts
    load(dbOrigin, dbDestination, 'income', 'income_b2b_real')
    load(dbOrigin, dbDestination, 'income', 'income_b2b_otb')
    load(dbOrigin, dbDestination, 'income', 'income_b2c_real')
    load(dbOrigin, dbDestination, 'income', 'income_b2c_otb')
    load(dbOrigin, dbDestination, 'income', 'income_forecast')
    load(dbOrigin, dbDestination, 'occupancy', 'occupancy')

  except Exception as e:
    # Error
    logger.error(e)
  
  finally:
    # Disconnect
    dbDestination.disconnect()
    dbOrigin.disconnect()

# ###################################################
# Startup
# ###################################################

if __name__ == '__main__':
  main()