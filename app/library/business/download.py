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
  clear('download')
 
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
    return 'facturas.zip'


# ##################################################
# Download contracts from Airflows
# ##################################################

def download_contracts(apiClient, variables=None):

  # Auth
  logger.info('Downloading contracts...')
  clear('download')
 
  # Get records (B2C bookings)
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
          id
        }
      }
      id
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

    # Services contract
    '''
    if item['resource'] and item['Contract_services']:
      name = 'Servicios (' + str(item['id']) + ') ' + str(item['resource']['building']['Name']) + ' ' + str(item['resource']['Code'][7:])
      file = apiClient.getFile(item['id'], 'Booking/Booking', 'Contract_services')
      with open('download/' + name + '.pdf', 'wb') as pdf:
        logger.info(name)
        num += 1
        pdf.write(file.content)
        pdf.close()
    '''

  # Get records (B2B group bookings)
  group_query = '''
  query Download ($fdesde:String, $fhasta:String) {
    data: Booking_Booking_groupList (
      where: {
        AND: [
          { Date_from: { GE: $fdesde } }
          { Date_from: { LT: $fhasta } }
        ]
      }
    ) {
      id
      Contract_rent { name }
      Contract_services { name }
      customer: CustomerViaPayer_id {
        Name
      }
    }
  }'''
  group_result = apiClient.call(group_query, variables)

  # Download each group file
  for item in group_result['data']:

    # Payer name (safe for file system)
    payer = str((item['customer'] or {}).get('Name') or '').replace('/', '-').replace('\\', '-').strip()

    # Rent contract
    if item['Contract_rent']:
      name = 'Renta B2B (' + str(item['id']) + ') ' + payer
      file = apiClient.getFile(item['id'], 'Booking/Booking_group', 'Contract_rent')
      with open('download/' + name + '.pdf', 'wb') as pdf:
        logger.info(name)
        num += 1
        pdf.write(file.content)
        pdf.close()

    # Services contract
    '''
    if item['Contract_services']:
      name = 'Servicios B2B (' + str(item['id']) + ') ' + payer
      file = apiClient.getFile(item['id'], 'Booking/Booking_group', 'Contract_services')
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
# Download CSVs N2
# ##################################################

def download_nra(dbClient, variables=None):

  # Auth
  logger.info('Downloading CSVs N2...')
  clear('download')

  # SQL
  sql = '''
    SELECT
      b.id,
      r."Code",
      substring(r."Registry_num", 11, 14) AS "CRU", 
      r."Registry_num" AS "NRUA",
      CASE 
        WHEN b."id" IS NULL THEN NULL
        WHEN b."Agent_id" IS NULL THEN NULL
        WHEN b."Reason_id" IN (5)    THEN 1 -- Vacacional
        WHEN b."Reason_id" IN (2, 4) THEN 2 -- Laboral
        WHEN b."Reason_id" IN (1, 3) THEN 3 -- Estudios
        ELSE NULL
      END AS "Reason", 
      CASE 
        WHEN b."id" IS NULL THEN NULL
        WHEN b."Agent_id" IS NULL THEN NULL
        ELSE 1
      END AS "Pax",
      CASE 
        WHEN b."id" IS NULL THEN NULL
        WHEN b."Agent_id" IS NULL THEN NULL
        ELSE GREATEST(b."Date_from"::date, make_date(%s, 1, 1))
      END AS "Date_from",
      CASE 
        WHEN b."id" IS NULL THEN NULL
        WHEN b."Agent_id" IS NULL THEN NULL
        ELSE LEAST(b."Date_to"::date, make_date(%s, 12, 31)) 
      END AS "Date_to",
      a."Name"
    FROM "Resource"."Resource" r 
      LEFT JOIN "Booking"."Booking" b ON r."id" = b."Resource_id"
        AND (
          b."Status" IN ('confirmada','firmacontrato','contrato','checkinconfirmado','checkin','inhouse','checkout','devolvergarantia','finalizada','revision')
          AND b."Date_from"::date <= make_date(%s, 12, 31)
          AND b."Date_to"::date   >= make_date(%s, 1, 1)
        )
      LEFT JOIN "Booking"."Customer_reason" cr ON cr."id" = b."Reason_id"
      LEFT JOIN "Provider"."Agent" a ON a."id" = b."Agent_id"
    ORDER BY 3, 2, 1
  '''

  # Capture exceptions
  try:

    # Get data
    year = variables['year'] or 2025
    con = dbClient.getconn()
    cur = dbClient.execute(con, sql, (year, year, year, year))
    data = cur.fetchall()
    cur.close()

    # Generate each CSV
    num = 0
    for item in data:

      # Valid NRUA
      nrua = item['NRUA']
      if nrua and len(nrua) == 53:

        # CSV Line
        line = ';'.join([
          nrua, 
          item['Date_from'].strftime('%Y-%m-%d') if item['Date_from'] else '', 
          item['Date_to'].strftime('%Y-%m-%d') if item['Date_to'] else '',
          str(item['Pax']) if item['Pax'] else '',
          str(item['Reason']) if item['Reason'] else '',
        ])

        # Write CSV file
        cru = item['CRU']
        if cru and len(cru) == 14:
          with open('download/n2/' + cru + '.csv', 'a') as csv:
            csv.write(line + '\n')
            num += 1

    # Zip
    if num > 0:
      zip('n2.zip', 'download')
      return 'n2.zip'

  # Error, return
  except Exception as e:
    logger.error(e)
    con.rollback()
    dbClient.putconn(con)
    return


# ##################################################
# Download
# ##################################################

def do_download(apiClient, dbClient, name, variables=None):

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
 
  # CSV N2
  elif name == 'nra':
    return download_nra(dbClient, variables)
 
  # Unknown
  else:
    return None
