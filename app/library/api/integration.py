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

def req_pub_int_clients():
  '''
    Retrieve newly created or updated customers
    ---
    parameters:
      - name: date
        in: query
        type: string
        required: false
        default: '2023-01-01'
      - name: Api-Key
        in: header
        type: string
        required: true
    definitions:
      Customer:
        type: object
        properties:
          id:
            type: integer
            format: int64        
          Third_party:
            type: boolean
          Type:
            type: string
          Document:
            type: string
          Email:
            type: string
            format: email
          Name:
            type: string
          Address:
            type: string
          City:
            type: string
          Province:
            type: string
          Zip:
            type: string
          Country:
            type: string
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
        description: Invalid API_KEY
  '''

  # Debug
  logger.debug('Integration - Clients')

  # Get API key
  print(request.headers)
  key = request.headers.get('Api-Key', None)
  print(key)
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