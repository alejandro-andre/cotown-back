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

# Cotown includes - services
from library.services.config import settings

# Cotown includes - business functions
from library.business.integration import q_int_clients

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
          description: "Bank account"
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
  if key != settings.SAP_API_KEY:
    logger.info('Invalid Api-Key: ' + str(key))
    abort(403, 'Invalid Api-Key')

  # Validate date
  date = '2023-01-01'
  d = request.args.get('date')
  if d != None:
    try:
      date = datetime.strptime(str(d), '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
      logger.info('Invalid date: ' + str(d))
      abort(400, 'Invalid date')

  # Return
  return q_int_clients(g.dbClient, date + ' 00:00:00')