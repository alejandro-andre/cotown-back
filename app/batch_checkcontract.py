# ###################################################
# Batch process
# ---------------------------------------------------
# Check contracts status
# ###################################################

# ###################################################
# Imports
# ###################################################

# Cotown includes
from library.services.config import settings
from library.services.apiclient import APIClient
from library.business.contract import check_contracts

# Logging
import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger('COTOWN')


# ###################################################
# Contract generator function
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
    file_handler = RotatingFileHandler('log/batch_printcontract.log', maxBytes=1000000, backupCount=5)
    file_handler.setLevel(settings.LOGLEVEL)
    file_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.info('Started')


    # ###################################################
    # GraphQL client
    # ###################################################

    # graphQL API
    apiClient = APIClient(settings.SERVER)
    apiClient.auth(user=settings.GQLUSER, password=settings.GQLPASS)


    # ###################################################
    # Main
    # ###################################################

    # Contract table and field
    TABLES = {'B2C':'Booking',       'B2B':'Booking_group', 'Annex':'Booking_group_annex' }
    FIELDS = {'B2C':'Contract_rent', 'B2B':'Contract_rent', 'Annex':'Contract_annex'      }

    # Contracts
    num = 0
    for key in TABLES:

      # Get pending individual booking contracts
      bookings = apiClient.call('''
      {
        data: Booking_''' + TABLES[key] + '''List (
          where: {
            AND: [
              { Contract_id: { NE: "n/a" } }
              { Contract_status: { NE: completed } }
              { Contract_status: { NE: voided } }
              { Contract_status: { NE: other } }
              { ''' + FIELDS[key] + ''': { IS_NULL: false } }
            ]
          }
        ) { 
          id 
          Contract_id 
          Contract_status
        }
      }
      ''')

      # Loop thru contracts
      if bookings is not None:
        for booking in bookings.get('data'):
            logger.debug(booking['id'])
            if check_contracts(apiClient, booking['Contract_id'], booking['Contract_status'], TABLES[key]):
              num += 1

    # Debug
    logger.info('{} contracts updated'.format(num))


# #####################################
# Main
# #####################################

if __name__ == '__main__':

    main()
    logger.info('Finished')
