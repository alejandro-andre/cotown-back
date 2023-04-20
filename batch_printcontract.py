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
from library.services.dbclient import DBClient
from library.services.apiclient import APIClient
from library.business.print_contract import do_contracts


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
    DATABASE = str(os.environ.get('COTOWN_DATABASE'))
    DBUSER   = str(os.environ.get('COTOWN_DBUSER'))
    DBPASS   = str(os.environ.get('COTOWN_DBPASS'))
    GQLUSER  = str(os.environ.get('COTOWN_GQLUSER'))
    GQLPASS  = str(os.environ.get('COTOWN_GQLPASS'))
    SSHUSER  = str(os.environ.get('COTOWN_SSHUSER'))
    SSHPASS  = str(os.environ.get('COTOWN_SSHPASS'))


    # ###################################################
    # GraphQL and DB client
    # ###################################################

    # graphQL API
    apiClient = APIClient(SERVER)
    apiClient.auth(user=GQLUSER, password=GQLPASS)

    # DB API
    dbClient = DBClient(SERVER, DATABASE, DBUSER, DBPASS, SSHUSER, SSHPASS)
    dbClient.connect()


    # ###################################################
    # Main
    # ###################################################

    # Get pending contracts
    bookings = apiClient.call('''
    {
      data: Booking_BookingList ( 
        orderBy: [{ attribute: id }]
        where: { 
          AND: [
            { Status: { EQ: firmacontrato } }, 
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


# #####################################
# Main
# #####################################

if __name__ == '__main__':

    main()