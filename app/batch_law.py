# ###################################################
# Batch process
# ---------------------------------------------------
# Calculates prices
# ###################################################

# ###################################################
# Imports
# ###################################################

# System includes
from datetime import date

# Cotown includes
from library.services.config import settings
from library.services.dbclient import DBClient

# Logging
import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger('COTOWN')


# ###################################################
# Loader function
# ###################################################

def main():

  # ###################################################
  # Logging
  # ###################################################

  logger.setLevel(settings.LOGLEVEL)
  formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(module)s] [%(funcName)s/%(lineno)d] [%(levelname)s] %(message)s')
  console_handler = logging.StreamHandler()
  console_handler.setLevel(settings.LOGLEVEL)
  console_handler.setFormatter(formatter)
  file_handler = RotatingFileHandler('log/batch_law.log', maxBytes=1000000, backupCount=5)
  file_handler.setLevel(settings.LOGLEVEL)
  file_handler.setFormatter(formatter)
  logger.addHandler(console_handler)
  logger.addHandler(file_handler)
  logger.info('Started')


  # ###################################################
  # DB client
  # ###################################################

  # DB API
  dbClient = DBClient(
    host=settings.SERVER,
    port=settings.get('DBPORT', 5432),
    dbname=settings.DATABASE,
    user=settings.DBUSER,
    password=settings.DBPASS,
    sshuser=settings.SSHUSER,
    sshpassword=settings.get('SSHPASS', None),
    sshprivatekey=settings.get('SSHPKEY', None)
  )
  dbClient.connect()
  con = dbClient.getconn()


  # ###################################################
  # Main
  # ###################################################

  # Get expenses
  cur = dbClient.execute(con, '''
    SELECT b."Code", COALESCE(b."Expense_IBI", 0) AS "Expense_IBI", COALESCE(b."Expense_HOA", 0) AS "Expense_HOA"
    FROM "Building"."Building" b
    ORDER BY 1
  ''')
  expenses = {code: {'ibi': ibi, 'hoa': hoa} for code, ibi, hoa in cur.fetchall()}
  cur.close()

  # Get resources
  cur = dbClient.execute(con, '''
    SELECT * FROM "Resource"."Resource" ORDER BY "Code" ASC
  ''')
  resources = cur.fetchall()
  cur.close()

  # Comparison constants
  two_years_ago = date.today().replace(year=date.today().year - 2)
  five_years_ago = date.today().replace(year=date.today().year - 5)

  # Loop thru resources
  num = 0
  status = ''
  building = None
  for resource in resources:

    # Pisos
    if resource['Resource_type'] == 'piso':

      # Building change?
      if building != resource['Code'][0:6]:
        building = resource['Code'][0:6]
        logger.info('Building %s', building)

      # Log flat
      logger.info('--Flat %s', resource['Code'])

      # Calculation fields
      renovation_date     = resource['Renovation_date']
      big_renovation_date = resource['Big_renovation_date']
      last_lau_date       = resource['Last_LAU_date']
      last_lau_rent       = resource['Last_LAU_rent'] or 0
      index_rent          = resource['Index_rent'] or 0
      weight              = resource['Weigth'] or 0
      area                = resource['Area'] or 0

      # Expenses
      max_expenses = float(expenses[building]['ibi'])
      if resource['HOA']:
        max_expenses += float(expenses[building]['hoa'])
      max_expenses *= (float(resource['Weigth'] or 0.0) / 100.0)

      # Big renovation < 5 years
      if big_renovation_date and big_renovation_date >= five_years_ago:
        status = 'libre'
  
      # > 150m, Not LAU or LAU > 5 years
      elif area >= 150 and (not last_lau_date or last_lau_date < five_years_ago):
        status = 'libre'
 
      # Not LAU or LAU > 5 years
      elif not last_lau_date or last_lau_date < five_years_ago:
        status = 'indice'

      # Lau < 5 years
      else:
        resource['Last_LAU_free_date'] = last_lau_date.replace(year=last_lau_date.year - 5)
        status = 'lau'

      # Calculate LAU rent
      if status == 'lau':
        lau_rent = last_lau_rent

        # Calculate IPC
        ipc = 1
        lau_rent *= ipc

        # 10% renovation
        if renovation_date and renovation_date >= two_years_ago:
          lau_rent *= 1.1

        # Check if index rent < LAU rent
        if index_rent < lau_rent:
          status = 'indice'

      # LAU Free date
      resource['Last_LAU_free_date'] = None
      if status != 'libre' and last_lau_date:
        resource['Last_LAU_free_date'] = last_lau_date.replace(year=last_lau_date.year - 5)

      # Libre
      if status == 'libre':
        resource['Limit_type']    = 'libre'
        resource['Max_rent']      = None
        resource['Max_expenses']  = None

      # Índice
      elif status == 'indice':
        resource['Limit_type']    = 'indice'
        resource['Max_rent']      = index_rent
        resource['Max_expenses']  = max_expenses

      # LAU
      else:
        resource['Limit_type']    = 'LAU'
        resource['Max_rent']      = lau_rent
        resource['Max_expenses']  = max_expenses

    # Habitación
    if resource['Resource_type'] in ('habitacion', 'plaza'):

      # Calculation fields
      weight = resource['Weigth'] or 0

      # Libre
      if status == 'libre':
        resource['Limit_type']    = 'libre'
        resource['Max_rent']      = None
        resource['Max_expenses']  = None

      # Índice
      elif status == 'indice':
        resource['Limit_type']    = 'indice'
        resource['Max_rent']      = index_rent * weight / 100
        resource['Max_expenses']  = max_expenses * weight / 100

      # LAU
      else:
        resource['Limit_type']    = 'LAU'
        resource['Max_rent']      = lau_rent * weight / 100
        resource['Max_expenses']  = max_expenses * weight / 100

    logger.info('{} {} {} {}'.format(
      resource['Code'],
      resource['Limit_type'],
      resource['Max_rent'],
      resource['Max_expenses']
    ))

    # Result
    num += 1

  # Info
  logger.info('{} resources processed'.format(num))


# #####################################
# Main
# #####################################

if __name__ == '__main__':

  main()
  logger.info('Finished')
