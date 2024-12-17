# ##################################################
# Imports
# ##################################################

# System imports
from zipfile import ZipFile
import os

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ##################################################
# Clear folder
# ##################################################

def clear(folder):

  for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    if os.path.isfile(file_path):
      os.remove(file_path)


# ##################################################
# Zip all files in folder
# ##################################################

def zip(name, folder):

  with ZipFile(name, 'w') as zip_file:
    for foldername, _, filenames in os.walk(folder):
      for filename in filenames:
        logger.info(filename)
        file_path = os.path.join(foldername, filename)
        zip_file.write(file_path, foldername[len(folder):] + '/' + filename)
        os.remove(file_path)
    return name


# ##################################################
# Download bills from Airflows
# ##################################################

def download_bills(apiClient, variables=None):

  # Auth
  logger.info('Downloading bills...')
 
  # Get records
  query = '''query Download ($fdesde:String, $fhasta:String, $pdesde:Int, $phasta:Int) {
    data: Billing_InvoiceList (
      where: {
        AND: [
          { Issued_date: { GE: $fdesde } }
          { Issued_date: { LT: $fhasta } }
          { Provider_id: { GE: $pdesde } }
          { Provider_id: { LE: $phasta } }
        ]
      }
    ) {
      id
      Code
      Bill_type
      Provider: ProviderViaProvider_id { Document }
      Document { name }
    }
  }'''
  result = apiClient.call(query, variables)

  # Download each file
  num = 0
  for item in result['data']:

    # Bill
    if item['Document']:
      name = item['Provider']['Document'] + '_' + item['Code']
      folder = 'recibos' if item['Bill_type'] == 'recibo' else 'facturas'
      file = apiClient.getFile(item['id'], 'Billing/Invoice', 'Document')
      with open('download/' + folder + '/' + name + '.pdf', 'wb') as pdf:
        logger.info(name)
        num += 1
        pdf.write(file.content)
        pdf.close()

  # Info
  logger.info('Downloaded {} bills'.format(num))

  # Zip
  if num > 0:
    zip('facturas.zip', 'download')
    clear('download/recibos')
    clear('download/facturas')
    return 'facturas.zip'


# ##################################################
# Download contracts from Airflows
# ##################################################

def download_contracts(apiClient, variables=None):

  # Auth
  logger.info('Downloading contracts...')
  clear('download')
 
  # Get records
  query = '''
  query Download ($fdesde:String, $fhasta:String, $pdesde:Int, $phasta:Int, $bdesde:Int, $bhasta:Int) {
    data: Booking_BookingList (
      where: {
        AND: [
          { Date_from: { GE: $fdesde } }
          { Date_from: { LT: $fhasta } }
          { Resource_id: { IS_NULL: false } }
        ]
      }
    ) {
      resource: ResourceViaResource_id {
        building: BuildingViaBuilding_id (
          joinType: INNER
          where: { 
            AND: [
              { id: { GE: $bdesde } }
              { id: { LE: $bhasta } }
            ]
          }
        ) {
          Name
        }
        Code
        ProviderViaOwner_id (
          joinType: INNER
          where: { 
            AND: [
              { id: { GE: $pdesde } }
              { id: { LE: $phasta } }
            ]
          }
        ) {
          Name
        }
      }
      id
      Contract_id
      Contract_status
      Contract_signed
      Contract_rent { name }
      Contract_services { name }
    }
  }'''
  result = apiClient.call(query, variables)

  # Download each file
  num = 0
  for item in result['data']:

    # Rent contract
    if item['resource'] and item['Contract_rent']:
      name = 'Renta (' + str(item['id']) + ') ' + str(item['resource']['building']['Name']) + ' ' + str(item['resource']['Code'][7:])
      file = apiClient.getFile(item['id'], 'Booking/Booking', 'Contract_rent')
      with open('download/' + name + '.pdf', 'wb') as pdf:
        logger.info(name)
        num += 1
        pdf.write(file.content)
        pdf.close()

    '''
    # Services contract
    if item['resource'] and item['Contract_services']:
      name = 'Servicios ' + str(item['resource']['building']['Name']) + ' ' + str(item['resource']['Code'][7:])
      file = apiClient.getFile(item['id'], 'Booking/Booking', 'Contract_services')
      with open('download/' + name + '.pdf', 'wb') as pdf:
        logger.info(name)
        num += 1
        pdf.write(file.content)
        pdf.close()
    '''

  # Info
  logger.info('Downloaded {} contracts'.format(num))

  # Zip
  if num > 0:
    zip('contratos.zip', 'download')
    return 'contratos.zip'


# ##################################################
# Download
# ##################################################

def do_download(apiClient, name, variables=None):

  # Variables
  if variables.get('fdesde') is None:
    variables['fdesde'] = '2023-01-01'
  if variables.get('fhasta') is None:
    variables['fhasta'] = '2099-12-31'
  if variables.get('pdesde') is None:
    variables['pdesde'] = 0
  if variables.get('phasta') is None:
    variables['phasta'] = 99999

  # Contracts
  if name == 'contratos':
    return download_contracts(apiClient, variables)
 
  # Bills
  elif name == 'facturas':
    return download_bills(apiClient, variables)
 
  # Unknown
  else:
    return None