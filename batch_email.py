# ###################################################
# Imports
# ###################################################

# System includes
import os

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Cotown includes
from library.dbclient import DBClient
from library.apiclient import APIClient


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

    # Get pending emails
    emails = apiClient.call('''
    {
      data: Customer_Customer_emailList ( 
        where: { 
          AND: [
            { Template: { IS_NULL: false } }
            { Subject: { IS_NULL: true } }
          ] 
        }
      ) {
        id
        Template
        Entity_id
      }
    }
    ''')

    # Loop thru contracts
    if emails is not None:
      for e in emails.get('data'):
          logger.debug(e)


# #####################################
# Main
# #####################################

if __name__ == '__main__':

    main()