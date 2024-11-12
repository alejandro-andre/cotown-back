# ###################################################
# API REST
# ---------------------------------------------------
# API access for SAP integration
# ###################################################

# ###################################################
# Imports
# ###################################################

# System includes
from flask import g, request, abort
from datetime import datetime
from schwifty import IBAN, exceptions

# Cotown includes - services
from library.services.config import settings

# Cotown includes - business functions
from library.business.integration import q_int_customers, q_int_invoices, q_int_management_fees

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Integration endpoints
# ###################################################

# ---------------------------------------------------
# Clients - Get recent clients
# ---------------------------------------------------

def req_pub_int_customers():
  '''
  Retrieve newly created or updated customers
  ---
  tags:
    - name: "Customers"
  parameters:
    - name: date
      in: query
      type: string
      required: false
      default: "2023-01-01"
      description: "Date from which new or modified customers are required, YYYY-MM-DD format"
    - name: Api-Key
      in: header
      type: string
      required: true
      description: "Security API KEY that must be present in the HTTP request header"
  definitions:
    Customer:
      type: object
      properties:
        id:
          type: integer
          format: int64        
          description: "Unique identifier in the system"
        third_party:
          type: boolean
          description: "Indicates if the customer is from a third party"
        type:
          type: string
          enum:
            - persona
            - empresa
          description: "Type of customer, individual or legal entity"
        document:
          type: string
          description: "Identity document / Tax identification"
        document_country:
          type: string
          description: "ISO Alpha-2 country code of the issuing country of the identity document"
        document_type:
          type: string
          enum:
            - DNI/NIF
            - NIE
            - CIF
            - Id Nacional
            - Pasaporte
          description: "Type of tax identification document"
        name:
          type: string
          description: "Customer's full name or the company's business name"
        address:
          type: string
          description: "Postal address: street, number, particles, etc."
        city:
          type: string
          description: "City of the postal address"
        province:
          type: string
          description: "Province, not mandatory"
        zip:
          type: string
          description: "Postal code of the postal address"
        country:
          type: string
          description: "ISO Alpha-2 country code of the postal address country"
        direct_debit_bank_account:
          type: string
          description: "IBAN or Bank account for direct debit"
        direct_debit_bank_code:
          type: string
          description: "Bank code from IBAN for direct_debit"
        bank_account:
          type: string
          description: "IBAN or Bank account for deposit return"
        bank_code:
          type: string
          description: "Bank code from IBAN for deposit return"
        swift:
          type: string
          description: "SWIFT or BIC code for deposit return"
        bank_holder:
          type: string
          description: "Bank holder"
        bank_name:
          type: string
          description: "Bank name"
        bank_address:
          type: string
          description: "Bank address"
        bank_city:
          type: string
          description: "Bank city"
        bank_country:
          type: string
          description: "Bank country ISO code"
  responses:
    200:
      description: List of created or updated customers since the given date
      content:
        application/json:
          schema:
            type: array
            items:
              $ref: '#/definitions/Customer'
    400:
      description: Invalid date or date format
    403:
      description: Invalid Api-Key
  '''

  # Debug
  logger.debug('Integration - Clients')

  # Get API key
  key = request.headers.get('Api-Key', None)
  client_data = settings.get(key)
  if not client_data:
    logger.warning('Invalid Api-Key: ' + str(key))
    abort(403, 'Invalid Api-Key')
  print(client_data)

  # Validate date
  date = '2023-01-01'
  d = request.args.get('date')
  if d != None:
    try:
      date = datetime.strptime(str(d), '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
      logger.warning('Invalid date: ' + str(d))
      abort(400, 'Invalid date')

  # Customers
  customers = q_int_customers(g.dbClient, date + ' 00:00:00', client_data.split(':'))

  # IBAN bank code
  for c in customers:
    try:
      iban = IBAN(c['bank_account'])
      c['bank_account'] = iban
      c['bank_code'] = iban.bank_code
      c['bank_name'] = iban.bank_name
      c['bank_country'] = iban.country_code
    except:
      c['bank_code'] = ''
    try:
      iban = IBAN(c['direc_debit_bank_account'])
      c['direc_debit_bank_account'] = iban
      c['direc_debit_bank_code'] = iban.bank_code
      c['direc_debit_bank_name'] = iban.bank_name
    except:
      c['direc_debit_bank_code'] = ''
      c['direc_debit_bank_name'] = ''

  # Return
  return customers


# ---------------------------------------------------
# Invoices - Get recent invoices
# ---------------------------------------------------

def req_pub_int_invoices():
  '''
  Retrieve newly issued invoices
  ---
  tags:
    - name: "Invoices"
  parameters:
    - name: date
      in: query
      type: string
      required: false
      default: "2023-01-01"
      description: "Issued minimum date, YYYY-MM-DD format"
    - name: Api-Key
      in: header
      type: string
      required: true
      description: "Security API KEY that must be present in the HTTP request header"
  definitions:
    Invoice:
      type: object
      properties:
        document_type:
          type: string
          description: "Type of document"
          enum:
            - CI
            - CCM
            - FT
            - AT
            - GF
        issuer_id:
          type: string
          description: "SAP Id of the company that issued the invoice"
        invoice_id:
          type: string
          description: "Id of the invoice"
        customer_id:
          type: integer
          format: int64        
          description: "SAP Id of the billed customer"
        currency:
          type: string
          description: "Currency of the invoice amounts, always 'EUR'"
        date:
          type: string
          description: "Invoice issued date"
        note:
          type: string
          description: "Comments"
        lines:
          type: array
          description: "Invoice lines"
          items:
            $ref: '#/definitions/Invoice_line'
    Invoice_line:
      type: object
      properties:
        service_id:
          type: string
          description: "SAP Id of the billed service"
        description:
          type: string
          description: "Description of the invoice content"
        project_id:
          type: string
          description: "SAP Id of the project/task to allocate the amount"
        amount:
          type: float
          description: "Amount of the billed service"
        tax_id:
          type: string
          description: "SAP Id of the tax applied"
        comments:
          type: string
          description: "Comments of the invoice line"
  responses:
    200:
      description: List of issued invoices since the given date
      content:
        application/json:
          schema:
            type: array
            items:
              $ref: '#/definitions/Invoice'
    400:
      description: Invalid date or date format
    403:
      description: Invalid Api-Key
  '''

  # Debug
  logger.debug('Integration - Invoices')

  # Get API key
  key = request.headers.get('Api-Key', None)
  client_data = settings.get(key)
  if not client_data:
    logger.warning('Invalid Api-Key: ' + str(key))
    abort(403, 'Invalid Api-Key')

  # Validate date
  date = '2024-01-01'
  d = request.args.get('date')
  if d != None:
    try:
      date = datetime.strptime(str(d), '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
      logger.warning('Invalid date: ' + str(d))
      abort(400, 'Invalid date')

  # Return
  return q_int_invoices(g.dbClient, date + ' 00:00:00', client_data.split(':'))


# ---------------------------------------------------
# Management fee
# ---------------------------------------------------

def req_pub_int_management_fees():
  '''
  Retrieve monthly management fees
  ---
  tags:
    - name: "Management fees"
  parameters:
    - name: month
      in: query
      type: string
      required: false
      default: "2024-01"
      description: "Month from which management fees are required, YYYY-MM format"
    - name: Api-Key
      in: header
      type: string
      required: true
      description: "Security API KEY that must be present in the HTTP request header"
  definitions:
    Fee:
      type: object
      properties:
        month:
          type: string
          description: "Management fees month"
        owner:
          type: string
          description: "SAP Id of the owner to be billed"
        resource:
          type: string
          description: "Building code"
        gross:
          type: float
          description: "Gross amount that the owner billed"
        net:
          type: float
          description: "Net amount that the owner billed"
        gross:
          type: float
          description: "Resulting amount of the fees"
  responses:
    200:
      description: Management fees by owner and building since the given date
      content:
        application/json:
          schema:
            type: array
            items:
              $ref: '#/definitions/Fee'
    400:
      description: Invalid month or month format
    403:
      description: Invalid Api-Key
  '''

  # Debug
  logger.debug('Integration - Management Fees')

  # Get API key
  key = request.headers.get('Api-Key', None)
  client_data = settings.get(key)
  if client_data != '0:9999':
    logger.warning('Invalid Api-Key: ' + str(key))
    abort(403, 'Invalid Api-Key')
  print(client_data)

  # Validate date
  d = request.args.get('month')
  if d == None:
    logger.warning('Empty month: ' + str(d))
    abort(400, 'Empty month')
  try:
    date = datetime.strptime(str(d) + '-01', '%Y-%m-%d').strftime('%Y-%m-%d')
  except ValueError:
    logger.warning('Invalid month: ' + str(d))
    abort(400, 'Invalid month')

  # Fees
  return q_int_management_fees(g.dbClient, date, client_data.split(':'))