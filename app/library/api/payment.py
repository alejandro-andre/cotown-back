# ###################################################
# API REST
# ---------------------------------------------------
# API access for Airflows buttons and logic
# ###################################################

# ###################################################
# Imports
# ###################################################

from flask import g, request, abort
from datetime import datetime
import urllib.parse

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
    if payment is None:
      abort(404)

    # Internal field, not part of the payment form response
    payment.pop('Payment_date', None)
 
    # Redsys data
    params = pay(
      pos       = payment['Pos'],
      order     = payment['Payment_order'],
      amount    = int(100 * float(payment['Amount'])),
      id        = payment['id'],
      urlok     = 'https://' + settings.CUSTOMER + '/#/pago_ok?id=' + payment['Payment_order'],
      urlko     = 'https://' + settings.CUSTOMER + '/#/pago_ko?id=' + payment['Payment_order'],
    )
    params['url']= settings.REDSYS_URL
    logger.debug(params)

    # Return both information
    return payment | params
 
# Notification
def req_pub_notification(pos='delegado'):

    # Validate response
    response = validate(pos, request.values)
    logger.debug(response)
    if response is None:
      return 'KO'

    # Transaction denied
    code = str(response.get('Ds_Response', ''))
    if not code.startswith('00'):
      logger.warning(f'Notificación Redsys ({pos}) denegada: Ds_Response {code}, pedido {response.get("Ds_Order")}')
      return 'KO'

    # Payment id
    try:
      id = int(urllib.parse.unquote(str(response['Ds_MerchantData'])))
    except (KeyError, TypeError, ValueError):
      logger.error(f'Notificación Redsys ({pos}) sin identificador de pago: {response.get("Ds_MerchantData")}, pedido {response.get("Ds_Order")}')
      return 'KO'

    # Get payment. Do not require the customer fiscal data: the money is already charged
    payment = q_get_payment(g.dbClient, id, validate_customer=False)
    logger.debug(payment)
    if payment is None:
      logger.error(f'Notificación Redsys ({pos}): no se encuentra el pago {id}, pedido {response.get("Ds_Order")}')
      return 'KO'

    # Already registered
    if payment['Payment_date'] is not None:
      logger.info(f'Notificación Redsys ({pos}): el pago {id} ya estaba registrado el {payment["Payment_date"]}')
      return 'OK'

    # Amount and currency checks. Only logged, the money is already charged
    try:
      amount = int(round(100 * float(payment['Amount'])))
      if int(response.get('Ds_Amount')) != amount:
        logger.error(f'Notificación Redsys ({pos}): el pago {id} se ha cobrado por {response.get("Ds_Amount")} y se esperaba {amount}')
    except (TypeError, ValueError):
      logger.error(f'Notificación Redsys ({pos}): el pago {id} trae un importe ilegible ({response.get("Ds_Amount")})')
    if str(response.get('Ds_Currency')) != '978':
      logger.error(f'Notificación Redsys ({pos}): el pago {id} se ha cobrado en la divisa {response.get("Ds_Currency")}')

    # Payment date check
    try:
      date = urllib.parse.unquote(response['Ds_Date'])
      hour = urllib.parse.unquote(response['Ds_Hour'])
      ts = date[6:] + '-' + date[3:5] + '-' + date[:2] + ' ' + hour + ':00'
      datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
    except Exception:
      ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      logger.error(f'Notificación Redsys ({pos}): el pago {id} no trae fecha válida ({response.get("Ds_Date")} {response.get("Ds_Hour")}), se registra con la fecha actual')
    logger.debug(ts)

    # Auth code
    auth = response.get('Ds_AuthorisationCode')
    if not auth:
      auth = 'REDSYS'
      logger.error(f'Notificación Redsys ({pos}): el pago {id} no trae código de autorización')

    # Update payment. Deny if it fails, so Redsys retries the notification
    if not q_put_payment(g.dbClient, id, auth, ts):
      logger.error(f'Notificación Redsys ({pos}): NO se ha podido registrar el cobro del pago {id} (auth {auth}, {ts})')
      return 'KO', 500

    # Ok
    return 'OK'
