# ###################################################
# Batch process
# ---------------------------------------------------
# Generates and sends emails
# ###################################################

# ###################################################
# Imports
# ###################################################

# Cotown includes
from library.services.config import settings
from library.services.apiclient import APIClient
from library.business.send_email import do_email

# Logging
import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger('COTOWN')


# ###################################################
# Email generator function
# ###################################################

def main():

  # ###################################################
  # Logging
  # ###################################################

  logger.setLevel(settings.LOGLEVEL)
  formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(module)s] [%(funcName)s/%(lineno)d] [%(levelname)s] %(message)s')
  console_handler = logging.StreamHandler()
  console_handler.setLevel(settings.LOGLEVEL)
  console_handler.setFormatter(formatter)
  file_handler = RotatingFileHandler('log/batch_sendemail.log', maxBytes=1000000, backupCount=5)
  file_handler.setLevel(settings.LOGLEVEL)
  file_handler.setFormatter(formatter)
  logger.addHandler(console_handler)
  logger.addHandler(file_handler)
  logger.info('Started')


  # ###################################################
  # GraphQL client
  # ###################################################

  # graphQL API
  apiClient = APIClient(settings.SERVER)
  apiClient.auth(user=settings.GQLUSER, password=settings.GQLPASS)


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
  num = 0
  for email in emails.get('data'):
    try:
      do_email(apiClient, email)
      num += 1
    except:
        pass
  logger.info('{} emails sent'.format(num))


# #####################################
# Main
# #####################################

if __name__ == '__main__':

  main()
  logger.info('Finished')
