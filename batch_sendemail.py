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
import markdown
import datetime

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Cotown includes
from library.services.apiclient import APIClient
from library.business.send_email import do_email, smtp_mail


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

      # Template? generate email body
      if email['Template'] is not None:
        subject, body = do_email(apiClient, email)
        
      # Manual email?
      else:
        subject = email['Subject']
        body = markdown.markdown(email['Body'], extensions=['tables', 'attr_list'])  

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

      # Debug
      if email['Customer']['Email'] != 'alejandroandref@gmail.com' and \
         email['Customer']['Email'] != 'cesar.ramos@experis.es':
         continue

      # Send email
      if subject != 'ERROR':
        logger.debug(email['Customer']['Email'])
        logger.debug(subject)
        logger.debug(body)
        smtp_mail(email['Customer']['Email'], subject, body)


# #####################################
# Main
# #####################################

if __name__ == '__main__':

    main()
