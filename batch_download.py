# ##################################################
# Imports
# ##################################################

# System includes

# Cotown includes
from library.services.apiclient import APIClient
from library.services.config import settings

# Logging
import logging
logger = logging.getLogger('COTOWN')


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


  # ##################################################
  # Download bills from Airflows
  # ##################################################

  def download_bills():

    # Auth
    logger.info('Downloading bills...')
    apiClient.auth(user=settings.GQLUSER, password=settings.GQLPASS)
    
    # Get records
    query = '''{ 
      data: Billing_InvoiceList { 
        id
        Code 
        Provider: ProviderViaProvider_id { 
          Document 
        } 
        Document { 
          oid 
          name 
        } 
      } 
    }'''
    result = apiClient.call(query)

    # Download each file
    num = 0
    for item in result['data']:

      # Bill
      if item['Document']:
        name = item['Provider']['Document'] + '-' + item['Code']
        file = apiClient.getFile(item['id'], 'Billing/Invoice', 'Document')
        with open('download/' + name + '.pdf', 'wb') as pdf:
          num += 1
          pdf.write(file.content)
          pdf.close()

    # Info
    logger.info('Downloaded {} bills'.format(num))


  # ##################################################
  # Download contracts from Airflows
  # ##################################################

  def download_contracts():

    # Auth
    logger.info('Downloading contracts...')
    apiClient.auth(user=settings.GQLUSER, password=settings.GQLPASS)
    
    # Get records
    query = '''{ 
      data: Booking_BookingList { 
        id
        Contract_rent { 
          oid 
          name 
        } 
        Contract_services { 
          oid 
          name 
        } 
      } 
    }'''
    result = apiClient.call(query)

    # Download each file
    num = 0
    for item in result['data']:

      # Rent contract
      if item['Contract_rent']:
        name = item['id'] + '-renta'
        file = apiClient.getFile(item['id'], 'Booking/Booking', 'Contract_rent')
        with open('download/' + name + '.pdf', 'wb') as pdf:
          pdf.write(file.content)
          pdf.close()

      # Rent services
      if item['Contract_services']:
        name = item['id'] + '-servicios'
        file = apiClient.getFile(item['id'], 'Booking/Booking', 'Contract_services')
        with open('download/' + name + '.pdf', 'wb') as pdf:
          pdf.write(file.content)
          pdf.close()
          num += 1

    # Info
    logger.info('Downloaded {} contracts'.format(num))


  # ##################################################
  # Download files
  # ##################################################

  download_bills()
  download_contracts()


# #####################################
# Main
# #####################################

if __name__ == '__main__':

  main()
  logger.info('Finished')
