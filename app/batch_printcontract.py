# ###################################################
# Batch process
# ---------------------------------------------------
# Generates PDF files from contracts
# ###################################################

# ###################################################
# Imports
# ###################################################

# Cotown includes
from library.services.config import settings
from library.services.apiclient import APIClient
from library.business.print_contract import do_contracts, do_group_contracts

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

    # Contracts
    num = 0

    # Get pending individual booking contracts
    date = settings.CONTRACTDATE
    bookings = apiClient.call('''
    {
      data: Booking_BookingList (
        where: {
          AND: [
            { Status: { IN: [firmacontrato, contrato, checkinconfirmado, checkin, inhouse] } },
            { Date_from: { GE: "''' + date + '''"} }
            { Contract_rent: { IS_NULL: true } }
          ]
        }
      ) { id }
    }
    ''')

    # Loop thru contracts
    if bookings is not None:
      for booking in bookings.get('data'):
          id = booking['id']
          logger.debug(id)
          if do_contracts(apiClient, id):
            num += 1

    # Get pending group booking contracts
    bookings = apiClient.call('''
    {
      data: Booking_Booking_groupList (
        orderBy: [{ attribute: id }]
        where: {
          AND: [
            { Status: { IN: [grupoconfirmado, inhouse] } },
            { Contract_rent: { IS_NULL: true } }
          ]
        }
      ) { id }
    }
    ''')

    # Loop thru contracts
    if bookings is not None:
      for booking in bookings.get('data'):
          id = booking['id']
          logger.debug(id)
          if do_group_contracts(apiClient, id):
            num += 1

    # Debug
    logger.info('{} contracts printed'.format(num))


# #####################################
# Main
# #####################################

if __name__ == '__main__':

    main()
    logger.info('Finished')
