# ###################################################
# DWH Scripts
# ---------------------------------------------------
# Create tables at DWH
# ###################################################

# ###################################################
# Imports
# ###################################################

# System imports
import os
import argparse
from datetime import datetime, timedelta

# Cotown includes
from library.services.dbclient import DBClient
from library.services.config import settings
from library.services.apiclient import APIClient
from library.business.load import load, execute
from library.business.occupancy import occupancy, beds
from library.business.forecast import forecast, budget
from library.business.gl import glSAP, glExcel

# Logging
import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger('COTOWN')

# ###################################################
# Connect to GraphQL
# ###################################################

def apiConnect():

# ---------------------------------------------------
# Connect to Core
# ---------------------------------------------------

  apiClient = APIClient(settings.DBHOST)
  apiClient.auth(user=settings.GQLUSER, password=settings.GQLPASS)
  return apiClient


# ###################################################
# Connect to BD
# ###################################################

def dbConnect():

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

def main(interfaces):

  # Connect
  try:
    dbOrigin, dbDestination = dbConnect()
    apiClient = apiConnect()
  except Exception as e:
    logger.error(e)
    return

  # Test
  if 'test' in interfaces:
    beds(dbOrigin)
    occupancy(dbOrigin)

  # Process
  try:

    # ------------------------------------
    # Init destination
    # ------------------------------------

    if 'init' in interfaces:
      execute(dbDestination, '_init')
    
    # ------------------------------------
    # General
    # ------------------------------------

    # Load dimensions
    if 'general' in interfaces:
      execute(dbDestination, '_clear_general')
      load(dbOrigin, dbDestination, 'owner', 'owner')
      load(dbOrigin, dbDestination, 'flat_type', 'flat_type')
      load(dbOrigin, dbDestination, 'place_type', 'place_type')
      load(dbOrigin, dbDestination, 'location', 'location')
      load(dbOrigin, dbDestination, 'product', 'product')
      load(dbOrigin, dbDestination, 'resource', 'resource')


    # ------------------------------------
    # SAP
    # ------------------------------------

    # Load dimensions
    if 'gl' in interfaces:
      # Clear
      execute(dbDestination, '_clear_gl')

      # Convert historic data
      #glExcel('CTS00-2023-00', 2023)
      #glExcel('CTS00-2024-00', 2024)
      
      # Extract current periods
      periods = []
      today = datetime.today()
      if today.day < 20:
        periods.append((today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m-01"))
      periods.append(today.strftime("%Y-%m-01"))

      # Get periods data
      for period in periods:
        glSAP(period,'ES02', 'CTS00', 'gl') # 'ES01', 'VDS0000001'

      # Load CSV files
      for file in os.listdir('csv'):
        if file.startswith('CTS00-') and file.endswith('.csv'):
          load(dbOrigin, dbDestination, 'gl', file[:-4])

    # ------------------------------------
    # Core
    # ------------------------------------

    # booking
    if 'booking' in interfaces:
      execute(dbDestination, '_clear_booking')
      load(dbOrigin, dbDestination, 'booking', 'booking')
      load(dbOrigin, dbDestination, 'marketplace', 'marketplace')

    # Income
    if 'income' in interfaces:
      forecast(apiClient)
      budget(apiClient)
      execute(dbDestination, '_clear_income')
      load(dbOrigin, dbDestination, 'income', 'income_budget')
      load(dbOrigin, dbDestination, 'income', 'income_forecast')
      load(dbOrigin, dbDestination, 'income', 'income_b2b_real')
      load(dbOrigin, dbDestination, 'income', 'income_b2b_otb')
      load(dbOrigin, dbDestination, 'income', 'income_b2c_real')
      load(dbOrigin, dbDestination, 'income', 'income_b2c_otb')
      load(dbOrigin, dbDestination, 'income', 'income_lau_real')
      load(dbOrigin, dbDestination, 'income', 'income_lau_otb')
      load(dbOrigin, dbDestination, 'income', 'mf_real')
      load(dbOrigin, dbDestination, 'income', 'mf_b2c_otb')
      load(dbOrigin, dbDestination, 'income', 'mf_b2b_otb')

    # Beds
    if 'beds' in interfaces:
      forecast(apiClient)
      beds(dbOrigin)
      execute(dbDestination, '_clear_beds')
      load(dbOrigin, dbDestination, 'beds', 'beds_forecast')
      load(dbOrigin, dbDestination, 'beds', 'beds_real')

    # Occupancy
    if 'occupancy' in interfaces:
      forecast(apiClient)
      occupancy(dbOrigin)
      execute(dbDestination, '_clear_occupancy')
      load(dbOrigin, dbDestination, 'occupancy', 'occupancy_forecast')
      load(dbOrigin, dbDestination, 'occupancy', 'occupancy_real')

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

  # Argument parser
  parser = argparse.ArgumentParser()
  parser.add_argument('--steps', nargs='+', help='ETL Steps to execute', required=True)
  args = parser.parse_args()

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

  logger.info(str(args.steps))
  main(args.steps)