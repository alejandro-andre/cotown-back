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

  # Get event
  event = request.json['event']
  id      = data['envelopeId']
  logger.info(event)
  logger.info(id)
  if event == 'envelope-removed':
    return 'ok'
  
  # Get data
  status  = data['envelopeSummary']['status']
  dt      = data['envelopeSummary']['statusChangedDateTime']
  subject = data['envelopeSummary']['emailSubject']
  if status not in ('sent', 'delivered', 'declined', 'completed', 'expired'):
    status = 'other'

  # Debug
  logger.info(subject)
  logger.info(status)
  logger.info(dt)
  #?q_change_contract(g.dbClient, id, dt, status)

  # Return
  return 'OK'
