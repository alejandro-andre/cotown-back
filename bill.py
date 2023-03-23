# ###################################################
# Imports
# ###################################################

# System includes
import os

# Cotown includes
from library.dbclient import DBClient
from library.apiclient import APIClient
from library.generate_bill import do_bill


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

    # Test
    SERVER   = 'experis.flows.ninja'
    DATABASE = 'niledb'
    DBUSER   = 'postgres'
    DBPASS   = 'postgres'
    GQLUSER  = 'modelsadmin'
    GQLPASS  = 'Ciber$2022'
    SSHUSER  = 'themes'
    SSHPASS  = 'Admin1234!'


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

    # Get pending billis
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

    # Loop thru contracts
    if bills  is not None:
      for b in bills.get('data'):
          id = b['id']
          print(id)
          do_bill(apiClient, id)


# #####################################
# Main
# #####################################

if __name__ == '__main__':

    main()