# ###################################################
# Batch process
# ---------------------------------------------------
# Generates PDF files from invoice records (bills 
# & receipts)
# ###################################################

# ###################################################
# Imports
# ###################################################

# Cotown includes
from library.services.config import settings
from library.services.apiclient import APIClient
from library.business.print_bill import do_bill

# Logging
import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger('COTOWN')


# ###################################################
# Bill generator function
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
  file_handler = RotatingFileHandler('log/batch_printbill.log', maxBytes=1000000, backupCount=5)
  file_handler.setLevel(settings.LOGLEVEL)
  file_handler.setFormatter(formatter)
  logger.addHandler(console_handler)
  logger.addHandler(file_handler)
  logger.info('Started')


  # ###################################################
  # GraphQL and DB client
  # ###################################################

  # graphQL API
  apiClient = APIClient(settings.SERVER)
  apiClient.auth(user=settings.GQLUSER, password=settings.GQLPASS)


  # ###################################################
  # Main
  # ###################################################

  # Get pending bills
  bills = apiClient.call('''
  {
    data: Billing_InvoiceList (
      where: {
        AND: [
          { Issued: { EQ: true } },
          { Document: { IS_NULL: true } }
        ]
      }
    ) { id }
  }
  ''')

  # Loop thru bills
  num = 0
  if bills  is not None:
    for b in bills.get('data'):
        id = b['id']
        logger.debug(id)
        if do_bill(apiClient, id):
          num += 1
  logger.info('{} bills printed'.format(num))


# #####################################
# Main
# #####################################

if __name__ == '__main__':

  main()
  logger.info('Finished')
