# ###################################################
# API REST
# ---------------------------------------------------
# Contract (docusign) functions
# ###################################################

# ###################################################
# Imports
# ###################################################
 
# System includes
from flask import g, request

# Cotown includes
from library.business.queries import q_change_contract

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Misc functions
# ###################################################

# Post
def req_pub_contract():

  # Get data
  data = request.json.get('data')
  if not data:
    return 'KO'

  # Get event info
  event  = request.json['event']
  status = data['envelopeSummary']['status']
  id     = data['envelopeId']
  dt     = data['envelopeSummary']['statusChangedDateTime']
  if status not in ('sent', 'delivered', 'declined', 'completed', 'expired'):
    status = 'other'

  # Debug
  logger.info(id)
  logger.info(dt)
  logger.info(event)
  logger.info(status)
  #?q_change_contract(g.dbClient, id, dt, status)

  # Return
  return 'OK'