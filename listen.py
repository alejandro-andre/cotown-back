# ###################################################
# Listen to new emails
# ---------------------------------------------------
# Listen to 'email' channel to send new emails
# ###################################################

# #####################################
# Imports
# #####################################

# System includes
import psycopg2
import time
import os

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Cotown includes
from library.services.apiclient import APIClient
from library.services.dbclient import DBClient
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

  # Listen to 'canal'
  psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
  dbClient.con.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
  dbClient.execute("LISTEN email")
  logger.info('Listening to ''email''...')

  # Infinite loop
  while dbClient.con.poll() == psycopg2.extensions.POLL_OK:

    # Wait for notification
    while dbClient.con.notifies:

      try:
        # Notification received
        notify = dbClient.con.notifies.pop(0)
        print(f"Mensaje recibido en el canal {notify.channel}: {notify.payload}")

        # Get email
        email = apiClient.call('''
          query EmailById ($id: Int!) {
            data: Customer_Customer_emailList ( 
              where: { id: { EQ: $id } }
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
            }
          }
          ''',
          { 'id': int(notify.payload) }
        )

        # Send email
        do_email(apiClient, email['data'][0])

      # Error
      except Exception as error:
        logger.error(error)

    # Wait X seconds
    time.sleep(5)

  # Close connection and tunnel
  dbClient.disconnect()


# #####################################
# Main
# #####################################

if __name__ == '__main__':

  main()