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
from library.business.integration import q_int_customers, q_int_invoices

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
        bank_account:
          type: string
          description: "IBAN or Bank account"
        bank_code:
          type: string
          description: "Bank code from IBAN"
        swift:
          type: string
          description: "SWIFT o r BIC code"
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
  #key = request.headers.get('Api-Key', None)
  #if key != settings.SAP_API_KEY:
  #  logger.info('Invalid Api-Key: ' + str(key))
  #  abort(403, 'Invalid Api-Key')

  # Validate date
  date = '2023-01-01'
  d = request.args.get('date')
  if d != None:
    try:
      date = datetime.strptime(str(d), '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
      logger.info('Invalid date: ' + str(d))
      abort(400, 'Invalid date')

  # Customers
  customers = q_int_customers(g.dbClient, date + ' 00:00:00')

  # IBAN bank code
  for c in customers:
    try:
      iban = IBAN(c['bank_account'])
      c['bank_account'] = iban
      c['bank_code'] = iban.bank_code
    except:
      c['bank_code'] = ''

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
  if key != settings.SAP_API_KEY:
    logger.info('Invalid Api-Key: ' + str(key))
    abort(403, 'Invalid Api-Key')

  # Validate date
  date = '2024-01-01'
  d = request.args.get('date')
  if d != None:
    try:
      date = datetime.strptime(str(d), '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
      logger.info('Invalid date: ' + str(d))
      abort(400, 'Invalid date')

  # Return
  return q_int_invoices(g.dbClient, date + ' 00:00:00')