# ###################################################
# Imports
# ###################################################

# System includes
import os

# Cotown includes
from library.dbclient import DBClient
from library.apiclient import APIClient
from library.generate_contract import do_contracts


# ###################################################
# Contract generator function
# ###################################################

def main():

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
            { Status: { EQ: confirmada } }, 
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
          print(id)
          do_contracts(apiClient, id)


# #####################################
# Main
# #####################################

if __name__ == '__main__':

    main()