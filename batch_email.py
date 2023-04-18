# ###################################################
# Imports
# ###################################################

# System includes
import os
import datetime

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Cotown includes
from library.dbclient import DBClient
from library.apiclient import APIClient
from library.email import smtp_mail
from library.generate_email import do_email


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

    # Get pending emails
    emails = apiClient.call('''
    {
      data: Customer_Customer_emailList ( 
        where: { 
          AND: [
            { Template: { IS_NULL: false } }
            { Subject: { IS_NULL: true } }
            { Sent_at: { IS_NULL: true } }
          ] 
        }
      ) {
        id
        Customer: CustomerViaCustomer_id {
          Name
          Address
          Email
        }
        Template
        Entity_id
      }
    }
    ''')

    # No emails
    if emails is None:
      return

    # Loop thru emails
    for email in emails.get('data'):

      # Debug
      logger.debug(email)

      # Generate email body
      subject, body = do_email(apiClient, email)

      # Update query
      query = '''
      mutation ($id: Int! $subject: String! $body: String! $sent: String!) {
        Customer_Customer_emailUpdate (
          where:  { id: {EQ: $id} }
          entity: { 
            Subject: $subject 
            Body: $body
            Sent_at: $sent
          }
        ) { id }
      }
      '''

      # Update variables
      variables = {
        'id': email['id'], 
        'subject': subject,
        'body': body,
        'sent': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
      }

      # Call graphQL endpoint
      apiClient.call(query, variables)

      # Send email
      logger.debug(email['Customer']['Email'])
      logger.debug(subject)
      logger.debug(body)
      smtp_mail(email['Customer']['Email'], subject, body)


# #####################################
# Main
# #####################################

if __name__ == '__main__':

    main()