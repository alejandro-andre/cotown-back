# ###################################################
# Batch process
# ---------------------------------------------------
# Generates PDF files from contracts
# ###################################################

# ###################################################
# Imports
# ###################################################

# System includes
import os

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Cotown includes
from library.services.apiclient import APIClient
from library.business.print_contract import do_contracts, do_group_contracts


# ###################################################
# Contract generator function
# ###################################################

def main():

    # ###################################################
    # Logging
    # ###################################################

    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(module)s] [%(levelname)s] %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.info('Started')


    # ###################################################
    # Environment variables
    # ###################################################

    SERVER   = str(os.environ.get('COTOWN_SERVER'))
    GQLUSER  = str(os.environ.get('COTOWN_GQLUSER'))
    GQLPASS  = str(os.environ.get('COTOWN_GQLPASS'))


    # ###################################################
    # GraphQL client
    # ###################################################

    # graphQL API
    apiClient = APIClient(SERVER)
    apiClient.auth(user=GQLUSER, password=GQLPASS)


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