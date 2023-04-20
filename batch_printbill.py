# ###################################################
# Batch process
# ---------------------------------------------------
# Generates PDF files from invoice records (bills  
# & receipts)
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
from library.business.print_bill import do_bill


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

    # Loop thru contracts
    if bills  is not None:
      for b in bills.get('data'):
          id = b['id']
          logger.debug(id)
          do_bill(apiClient, id)


# #####################################
# Main
# #####################################

if __name__ == '__main__':

    main()