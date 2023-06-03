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
logger = logging.getLogger('COTOWN')


# ###################################################
# Contract generator function
# ###################################################

def main():

    # ###################################################
    # Logging
    # ###################################################

    logger.setLevel(settings.LOGLEVEL)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(settings.LOGLEVEL)
    formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(module)s] [%(levelname)s] %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
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

    # Get pending individual booking contracts
    bookings = apiClient.call('''
    {
      data: Booking_BookingList ( 
        where: { 
          AND: [
            { Status: { IN: [firmacontrato, contrato, checkinconfirmado, checkin, inhouse] } },
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
          do_contracts(apiClient, id)

    # Get pending group booking contracts
    bookings = apiClient.call('''
    {
      data: Booking_Booking_groupList ( 
        orderBy: [{ attribute: id }]
        where: { 
          AND: [
            { Status: { EQ: grupoconfirmado } }, 
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
          do_group_contracts(apiClient, id)


# #####################################
# Main
# #####################################

if __name__ == '__main__':

    main()