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

def req_int_clients():

  # Debug
  logger.debug('Integration - Clients')

  # Get API key
  #key = request.headers.get('API_KEY', None)
  #if key != settings.SAP_API_KEY:
  #  logger.info('Invalid API KEY: ' + str(key))
  #  abort(403, 'Invalid API KEY')

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