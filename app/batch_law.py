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
from dateutil.relativedelta import relativedelta


# Cotown includes
from library.services.config import settings
from library.services.dbclient import DBClient

# Logging
import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger('COTOWN')


from datetime import date
from typing import List, Tuple

# ###################################################
# Cumulative IPC
# ###################################################


def cumulative_cpi(target_date, cpi_data) -> float:
  # Today
  today = date.today()

  # Current month
  month = target_date.month

  # Group by year, keeping the latest entry per year for the target month
  by_year: dict[int, Tuple[date, float]] = {}
  for d, value in cpi_data:
      if d.month != month or d.year <= target_date.year or d > today:
          continue
      if d.year not in by_year or d > by_year[d.year][0]:
          by_year[d.year] = (d, float(value))

  # Compound product sorted by year
  result = 1.0
  for _, value in sorted(by_year.values()):
      result *= 1 + value / 100

  # Return cumulative IPC
  return result


# ###################################################
# Main function
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

  # Get IPC
  cur_read = dbClient.execute(con, '''
    SELECT "Date_IPC", "Value_IPC" FROM "Auxiliar"."Ipc" ORDER BY 1
  ''')
  ipcs = cur_read.fetchall()
  cur_read.close()

  # Get expenses
  cur_read = dbClient.execute(con, '''
    SELECT b."Code", COALESCE(b."Expense_IBI", 0) AS "Expense_IBI", COALESCE(b."Expense_HOA", 0) AS "Expense_HOA"
    FROM "Building"."Building" b
    ORDER BY 1
  ''')
  expenses = {code: {'ibi': ibi, 'hoa': hoa} for code, ibi, hoa in cur_read.fetchall()}
  cur_read.close()

  # Get resources
  cur_read = dbClient.execute(con, '''
    SELECT r."Code", d."Location_id", COALESCE(p."Total_Weight", r."Weigth") AS "Weight", *
    FROM "Resource"."Resource" r
    LEFT JOIN (
      SELECT "Room_id", SUM("Weigth") AS "Total_Weight"
        FROM "Resource"."Resource"
        WHERE "Resource_type" = 'plaza'
        GROUP BY "Room_id"
    ) p ON r."id" = p."Room_id"
    JOIN "Building"."Building" b on b.id = r."Building_id"
    join "Geo"."District" d on d.id = b."District_id" 
    WHERE r."Resource_type" IN ('piso', 'habitacion', 'plaza')
    ORDER BY r."Code" ASC
  ''')
  resources = cur_read.fetchall()
  cur_read.close()

  # Write cursor
  cur_write = con.cursor()

  # Comparison constants
  two_years_ago = date.today().replace(year=date.today().year - 2)
  five_years_ago = date.today().replace(year=date.today().year - 5)

  # Loop thru resources
  num = 0
  ipc = 1
  status = ''
  building = None
  for resource in resources:

    # Pisos
    if resource['Resource_type'] == 'piso':

      # Default limit type
      status = 'lau'
    
      # Building change?
      if building != resource['Code'][0:6]:
        building = resource['Code'][0:6]
        #logger.info('Building %s', building)

      # Log flat
      #logger.info('--Flat %s', resource['Code'])

      # Calculation fields
      renovation_date     = resource['Renovation_date']
      big_renovation_date = resource['Big_renovation_date']
      last_lau_date       = resource['Last_LAU_date']
      last_lau_rent       = float(resource['Last_LAU_rent'] or 0)
      index_rent          = float(resource['Index_rent'] or 0)
      weight              = float(resource['Weight'] or 0)
      area                = float(resource['Area_woc'] or 0)

      # Expenses
      max_expenses = (float(expenses[building]['ibi']) + float(expenses[building]['hoa'])) * weight / 12 / 100.0 if resource['HOA'] else 0

      # Not in Barcelona
      if resource["Location_id"] != 1:
        status = 'libre'

      # Big renovation < 5 years
      elif big_renovation_date and big_renovation_date >= five_years_ago:
        status = 'libre'
  
      # > 150m, Not LAU or LAU > 5 years
      elif area >= 150 and (not last_lau_date or last_lau_date < five_years_ago):
        status = 'libre'
 
      # Not LAU or LAU > 5 years
      elif not last_lau_date or last_lau_date < five_years_ago or last_lau_rent == 0:
        status = 'indice'

      # Lau < 5 years
      else:
        resource['Last_LAU_free_date'] = last_lau_date + relativedelta(years=5)

      # Calculate LAU rent
      if status == 'lau':

        # Calculate IPC
        ipc = cumulative_cpi(last_lau_date, ipcs)
        last_lau_rent *= ipc

        # 10% renovation
        if renovation_date and renovation_date >= two_years_ago:
          last_lau_rent *= 1.1

        # Check if index rent < LAU rent
        if index_rent > 0 and index_rent < last_lau_rent:
          status = 'indice'

      # Not LAU nor index
      if status == 'indice' and index_rent == 0:
        status = 'libre'  

      # LAU Free date
      resource['Last_LAU_free_date'] = None
      if status != 'libre' and last_lau_date:
        resource['Last_LAU_free_date'] = last_lau_date + relativedelta(years=5)

      # Libre
      if status == 'libre':
        resource['Limit_type']    = 'libre'
        resource['Max_LAU_rent']  = None
        resource['Max_rent']      = None
        resource['Max_expenses']  = None

      # Índice
      elif status == 'indice':
        resource['Limit_type']    = 'indice'
        resource['Max_LAU_rent']  = round(last_lau_rent, 2)
        resource['Max_rent']      = round(index_rent, 2)
        resource['Max_expenses']  = round(max_expenses, 2)

      # LAU
      else:
        resource['Limit_type']    = 'lau'
        resource['Max_LAU_rent']  = round(last_lau_rent, 2)
        resource['Max_rent']      = round(last_lau_rent, 2)
        resource['Max_expenses']  = round(max_expenses, 2)

    # Habitación
    if resource['Resource_type'] in ('habitacion', 'plaza'):

      # Calculation fields
      weight = float(resource['Weight'] or 0)

      # Libre
      if status == 'libre':
        resource['Limit_type']    = 'libre'
        resource['Max_LAU_rent']  = None
        resource['Max_rent']      = None
        resource['Max_expenses']  = None

      # Índice
      elif status == 'indice':
        resource['Limit_type']    = 'indice'
        resource['Max_LAU_rent']  = round(last_lau_rent * weight / 100, 2)
        resource['Max_rent']      = round(index_rent * weight / 100, 2)
        resource['Max_expenses']  = round(max_expenses * weight / 100, 2)

      # LAU
      else:
        resource['Limit_type']    = 'lau'
        resource['Max_LAU_rent']  = round(last_lau_rent * weight / 100, 2)
        resource['Max_rent']      = round(last_lau_rent * weight / 100, 2)
        resource['Max_expenses']  = 0

    # Update
    cur_write.execute('''
      UPDATE "Resource"."Resource" 
      SET "Last_LAU_free_date" = %s, "Limit_type" = %s, "Max_LAU_rent" = %s, "Max_rent" = %s, "Max_expenses" = %s 
      WHERE id = %s''', 
      (
        resource['Last_LAU_free_date'],
        resource['Limit_type'],
        resource['Max_LAU_rent'],
        resource['Max_rent'],
        resource['Max_expenses'],
        resource['id'],
      )
    )
    logger.info('{} {} {} {} {} {} {} {} {}'.format(
      resource['Code'],
      ipc,
      resource['Limit_type'],
      resource['Last_LAU_rent'],
      resource['Index_rent'],
      resource['Weight'],
      resource['Max_LAU_rent'],
      resource['Max_rent'],
      resource['Max_expenses']
    ))

    # Result
    num += 1

  # Commit
  con.commit()
  cur_write.close()
  logger.info('{} resources processed'.format(num))


# #####################################
# Main
# #####################################

if __name__ == '__main__':

  main()
  logger.info('Finished')
