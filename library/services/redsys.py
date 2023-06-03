# #############################################
# Imports
# #############################################

from Crypto.Cipher import DES3
import logging
import json
import base64
import hmac
import hashlib

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Cotown includes
from library.services.config import settings

# #####################################
# 3DES cypher
# # #####################################

def encrypt_DES3(order: str) -> bytes:

  secret_key: bytes = settings.REDSYS_KEY.encode('utf-8')
  key = base64.b64decode(secret_key)
  cipher = DES3.new(key, DES3.MODE_CBC, IV=b'\0\0\0\0\0\0\0\0')
  return cipher.encrypt(order.encode('utf-8').ljust(16, b'\0'))


def calc_signature(order, params):

  # Diversify key
  secret_key: bytes = settings.MERCHANT_KEY.encode('utf-8')
  cipher = DES3.new(base64.b64decode(secret_key), DES3.MODE_CBC, IV=b'\0\0\0\0\0\0\0\0')
  key = cipher.encrypt(order.encode('utf-8').ljust(16, b'\0'))

  # Signature
  signature = base64.b64encode(hmac.new(key, params, hashlib.sha256).digest())
  return signature


# #####################################
# Payment form
# #####################################

def pay(order, amount, id, urlok, urlko):

  # Transaction data
  data = {
    'DS_MERCHANT_CURRENCY'       : '978', # Euro
    'DS_MERCHANT_TRANSACTIONTYPE': '0', # Pago
    'DS_MERCHANT_TERMINAL'       : settings.REDSYS_TERMINAL,
    'DS_MERCHANT_MERCHANTCODE'   : settings.REDSYS_MERCHANTCODE,
    'DS_MERCHANT_MERCHANTURL'    : settings.REDSYS_MERCHANTURL,
    'DS_MERCHANT_URLOK'          : urlok,
    'DS_MERCHANT_URLKO'          : urlko,
    'DS_MERCHANT_MERCHANTDATA'   : str(id),
    'DS_MERCHANT_ORDER'          : str(order),
    'DS_MERCHANT_AMOUNT'         : str(amount)
  }

  # Merchant parameters
  text = json.dumps(data).replace(' ', '').replace('\n', '')
  params = base64.b64encode(text.encode('utf-8'))
  logger.debug(data)
  logger.debug(params.decode('utf-8'))

  # Signature
  signature = calc_signature(order, params)
  logger.debug(signature.decode('utf-8'))

  #<html>
  #<form name="from" action="https://sis-t.redsys.es:25443/sis/realizarPago" method="POST" target="_top">
  #<input type="hidden" name="Ds_SignatureVersion" value="HMAC_SHA256_V1"/>
  #<input type="hidden" name="Ds_MerchantParameters" value="{}"/>
  #<input type="hidden" name="Ds_Signature" value="{}"/>
  #<input type="submit">
  #</form>
  #</html>
  
  return {
    'Ds_MerchantParameters': params.decode('utf-8'), 
    'Ds_Signature': signature.decode('utf-8'), 
    'Ds_SignatureVersion': 'HMAC_SHA256_V1'
  }


# #####################################
# Validate payment
# #####################################

def validate(response):

  # Received params
  params = response['Ds_MerchantParameters']
  logger.debug(params)

  # Get DS_ORDER
  result = json.loads(base64.b64decode(params).decode('utf-8'))
  logger.debug(result)

  # Calc signatures
  calculated_signature = calc_signature(result['Ds_Order'], params.encode('utf-8')).decode('utf-8')
  received_signature = response['Ds_Signature'].replace('_', '/').replace('-', '+')
  logger.debug(calculated_signature)
  logger.debug(received_signature)
  
  # Check signature
  if calculated_signature != received_signature:
    logger.debug('Dont match')
    return None
  
  # Return response
  return result
