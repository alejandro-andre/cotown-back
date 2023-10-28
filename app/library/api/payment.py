# ###################################################
# API REST
# ---------------------------------------------------
# API access for Airflows buttons and logic
# ###################################################

# ###################################################
# Imports
# ###################################################

from flask import g, request, abort

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Cotown includes - services
from library.services.redsys import pay, validate
from library.services.config import settings

# Cotown includes - business functions
from library.business.queries import q_get_payment, q_put_payment


# ###################################################
# Payments
# ###################################################

# Prepare payment params
def req_pay(id):

    # Get payment
    payment = q_get_payment(g.dbClient, id, generate_order=True)
    logger.debug(payment)
    logger.debug(payment)
    if payment is None:
      abort(404)
  
    # Redsys data
    params = pay(
      order     = payment['Payment_order'], 
      amount    = int(100 * float(payment['Amount'])), 
      id        = payment['id'],
      urlok     = 'https://' + settings.BACK + '/customer/#/pago_ok?id=' + payment['Payment_order'],
      urlko     = 'https://' + settings.BACK + '/customer/#/pago_ko?id=' + payment['Payment_order'],
    )
    params['url']= settings.REDSYS_URL
    logger.debug(params)

    # Return both information
    return payment | params 
  
# Notification
def req_notification():

    # Validate response
    response = validate(request.values)
    if response is None:
      return 'OK'

    # Transaction denied
    if response['Ds_Response'][:2] != '00':
      return 'KO'

    # Get payment
    id = int(response['Ds_MerchantData'])
    payment = q_get_payment(g.dbClient, id)
    logger.debug(payment)
    if payment is None:
      return 'KO'

    # Update payment
    date = response['Ds_Date']
    hour = response['Ds_Hour']
    ts = date[6:] + '-' + date[3:5] + '-' + date[:2] + ' ' + hour + ':00'
    logger.debug(ts)
    q_put_payment(g.dbClient, id, response['Ds_AuthorisationCode'], ts)

    # Ok
    return 'OK'