# ###################################################
# Batch process
# ---------------------------------------------------
# Generates and sends emails
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
from library.business.send_email import do_email


# ###################################################
# Email generator function
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

    # Get pending emails
    emails = apiClient.call('''
    {
      data: Customer_Customer_emailList ( 
        where: { Sent_at: { IS_NULL: true } }
      ) {
        id
        Customer: CustomerViaCustomer_id {
          Name
          Address
          Email
          Lang
        }
        Template
        Entity_id
        Subject
        Body
        Sent_at
      }
    }
    ''')

    # No emails
    if emails is None:
      return

    # Loop thru emails
    for email in emails.get('data'):
      do_email(apiClient, email)


# #####################################
# Main
# #####################################

if __name__ == '__main__':

    main()
