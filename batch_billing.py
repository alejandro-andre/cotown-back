# ###################################################
# Batch process
# ---------------------------------------------------
# Billing process
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


# ###################################################
# Bill generator function
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
    # GraphQL and DB client
    # ###################################################

    # graphQL API
    apiClient = APIClient(SERVER)
    apiClient.auth(user=GQLUSER, password=GQLPASS)


    # ###################################################
    # Main
    # ###################################################

    # 1. Generate invoice for each booking fee payment 
    #    Get every booking fee payment without bill
    pass

    # 2. Generate recepit for each deposit payment 
    #    Get every deposit payment without bill
    pass

    # 3. Monthly billing process
    #    Process each inhouse booking
    pass


# #####################################
# Main
# #####################################

if __name__ == '__main__':

    main()