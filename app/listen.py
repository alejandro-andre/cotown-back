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

# Cotown includes
from library.services.config import settings
from library.services.apiclient import APIClient
from library.services.dbclient import DBClient
from library.business.send_email import do_email

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Email generator function
# ###################################################

def main():

  # ###################################################
  # Logging
  # ###################################################

  logger.setLevel(settings.LOGLEVEL)
  console_handler = logging.StreamHandler()
  console_handler.setLevel(settings.LOGLEVEL)
  formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(module)s] [%(funcName)s/%(lineno)d] [%(levelname)s] %(message)s')
  console_handler.setFormatter(formatter)
  logger.addHandler(console_handler)
  logger.info('Started')


  # ###################################################
  # GraphQL and DB client
  # ###################################################

  # graphQL API
  apiClient = APIClient(settings.SERVER)

  # DB API
  dbClient = DBClient(
    host=settings.SERVER,
    port=settings.get('DBPORT', 5432),
    dbname=settings.DATABASE,
    user=settings.DBUSER,
    password=settings.DBPASS,
    sshuser=settings.SSHUSER,
    sshpassword=settings.get('SSHPASS', None),
    sshprivatekey=settings.get('SSHPKEY', None)
  )

  # ###################################################
  # Main
  # ###################################################

  # Infinite loop
  while True:

    # Manage any exception
    try:

      # Connect
      logger.info('Connecting...')
      dbClient.connect()
      con = dbClient.getconn()

      # Listen to 'canal'
      psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
      con.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
      dbClient.execute(con, 'LISTEN email')
      logger.info('Listening to ''email''...')

      # Infinite loop
      while con.poll() == psycopg2.extensions.POLL_OK:

        # Wait for notification
        while con.notifies:

          # Notification received
          notify = con.notifies.pop(0)
          logger.info(f'Mensaje recibido en el canal {notify.channel}: {notify.payload}')

          # Get email
          apiClient.auth(user=settings.GQLUSER, password=settings.GQLPASS)
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
                Cc
                Cco
                Sent_at
              }
            }
            ''',
            { 'id': int(notify.payload) }
          )

          # Send email
          do_email(apiClient, email['data'][0])

        # Wait 10 seconds
        time.sleep(10)

    # Error
    except Exception as error:     
      logger.error(error)
      con.rollback()

    # Close connection and tunnel
    dbClient.putconn(con)
    dbClient.disconnect()

    # Wait 30 seconds and try to connect again
    time.sleep(30)
    logger.info('Trying again...')


# #####################################
# Main
# #####################################

if __name__ == '__main__':

  main()