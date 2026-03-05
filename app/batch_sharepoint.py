# ###################################################
# Batch process
# ---------------------------------------------------
# Downloads and shares bills
# ###################################################

# ###################################################
# Imports
# ###################################################

# System imports
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Cotown includes
from library.services.config import settings
from library.services.apiclient import APIClient

# Logging
import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger('COTOWN')


# ###################################################
# Logging
# ###################################################

logger.setLevel(settings.LOGLEVEL)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(module)s] [%(funcName)s/%(lineno)d] [%(levelname)s] %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(settings.LOGLEVEL)
console_handler.setFormatter(formatter)
file_handler = RotatingFileHandler('log/batch_sharepoint.log', maxBytes=1000000, backupCount=5)
file_handler.setLevel(settings.LOGLEVEL)
file_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.info('Started')


# ###################################################
# Bill downloader
# ###################################################

def main(variables):

  # ###################################################
  # GraphQL client
  # ###################################################

  # graphQL API
  apiClient = APIClient(settings.SERVER)
  apiClient.auth(user=settings.GQLUSER, password=settings.GQLPASS)


  # ###################################################
  # Main
  # ###################################################

  # Get records
  query = '''
  query Download ($fdesde:String, $fhasta:String) {
    data: Billing_InvoiceList (
      where: {
        AND: [
          { Issued_date: { GE: $fdesde } }
          { Issued_date: { LT: $fhasta } }
        ]
      }
    ) {
      id
      Code
      Issued_date
      Bill_type
      Provider: ProviderViaProvider_id { 
        Name
        Document 
      }
      Lines: Invoice_lineListViaInvoice_id {
        Resource: ResourceViaResource_id {
          Code
        }
      }
      Document { 
        name 
      }
    }
  }
  '''
  result = apiClient.call(query, variables)

  # Download each file
  num = 0
  for item in result['data']:

    # Bill
    if item['Document']:
      # File name
      resource = item['Lines'][0]['Resource']['Code']
      name     = resource[:12] + '-' + item['Code']
      folder   = ('Recibos' if item['Bill_type'] == 'recibo' else 'Facturas') \
               + '/' + item['Provider']['Name'].split(',')[0] \
               + '/' + item['Issued_date'].split('-')[0] \
               + '/' + item['Issued_date'].split('-')[1] \
               + '/' + resource[:6]

      # Create path
      path = Path('sharepoint') / folder
      path.mkdir(parents=True, exist_ok=True)

      # Get and save file
      file = apiClient.getFile(item['id'], 'Billing/Invoice', 'Document')
      with open('sharepoint/' + folder + '/' + name + '.pdf', 'wb') as pdf:
        logger.info(folder + '/' + name + '.pdf')
        pdf.write(file.content)
        pdf.close()
      num += 1

  # Info
  logger.info('Downloaded {} bills'.format(num))


# #####################################
# Main
# #####################################

if __name__ == '__main__':
  # Parse args
  parser = argparse.ArgumentParser(description="Download bills")
  parser.add_argument("--fdesde", type=str, help="Fecha desde (YYYY-MM-DD)")
  parser.add_argument("--fhasta", type=str, help="Fecha hasta (YYYY-MM-DD)")
  args = parser.parse_args()

  # Default values
  if args.fdesde and args.fhasta:
    fdesde = args.fdesde
    fhasta = args.fhasta
  else:
    today = datetime.today().date()
    fdesde = (today - timedelta(days=2)).isoformat()
    fhasta = (today + timedelta(days=1)).isoformat()

  # Run
  logger.info('Downloading bills from ' + fdesde + ' to ' + fhasta + '...')
  main({'fdesde': fdesde, 'fhasta': fhasta})
  logger.info('Finished')