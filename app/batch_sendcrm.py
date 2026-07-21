# ###################################################
# Batch process
# ---------------------------------------------------
# Sends new bookings to the CRM (Pipedrive)
# ###################################################

# ###################################################
# Imports
# ###################################################

# Cotown includes
from library.services.config import settings
from library.services.dbclient import DBClient
from library.business.send_crm import q_pending_leads, do_crm

# Logging
import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger('COTOWN')


# ###################################################
# CRM sender function
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
  file_handler = RotatingFileHandler('log/batch_sendcrm.log', maxBytes=1000000, backupCount=5)
  file_handler.setLevel(settings.LOGLEVEL)
  file_handler.setFormatter(formatter)
  logger.addHandler(console_handler)
  logger.addHandler(file_handler)
  logger.info('Started')


  # ###################################################
  # DB client
  # ###################################################

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

  # Get pending bookings
  leads = q_pending_leads(dbClient, con)

  # Loop thru bookings
  num = 0
  for lead in leads:
    try:
      num += do_crm(dbClient, con, lead)
    except Exception as err:
      logger.error(err)
      con.rollback()
  logger.info('{} bookings sent to CRM'.format(num))

  # Disconnect
  dbClient.putconn(con)
  dbClient.disconnect()


# #####################################
# Main
# #####################################

if __name__ == '__main__':

  main()
  logger.info('Finished')
