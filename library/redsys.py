# #############################################
# Imports
# #############################################

from Crypto.Cipher import DES3
import json
import base64
import hmac
import hashlib

# #############################################
# Constants
# #############################################

SERVER                   = 'dev.cotown.ciber.es'

MERCHANT_CURRENCY        = '978'       # Euro
MERCHANT_MERCHANTCODE    = '348032921' # Test
MERCHANT_TERMINAL        = '002'       # Terminal 1
MERCHANT_TRANSACTION_PAY = '0'         # Pago
MERCHANT_MERCHANTURL     = 'https://' + SERVER + '/notificacion'
MERCHANT_URLOK           = 'https://' + SERVER + '/ok?op='
MERCHANT_URLKO           = 'https://' + SERVER + '/ko?op='
MERCHANT_KEY             = 'sq7HjrUOBfKmC576ILgskD5srU870gJ7'

# Test
#MERCHANT_URLOK           = 'https://experis.flows.ninja/admin/Test.PagoOK/external?op='
#MERCHANT_URLKO           = 'https://experis.flows.ninja/admin/Test.PagoOK/external?op='

data = {
 'DS_MERCHANT_CURRENCY': MERCHANT_CURRENCY,
 'DS_MERCHANT_MERCHANTCODE': MERCHANT_MERCHANTCODE,
 'DS_MERCHANT_MERCHANTURL': MERCHANT_MERCHANTURL,
 'DS_MERCHANT_TERMINAL': MERCHANT_TERMINAL,
 'DS_MERCHANT_TRANSACTIONTYPE': MERCHANT_TRANSACTION_PAY,
}


# #####################################
# 3DES cypher
# # #####################################

def encrypt_DES3(order: str) -> bytes:

    secret_key: bytes = MERCHANT_KEY.encode()
    key = base64.b64decode(secret_key)
    cipher = DES3.new(key, DES3.MODE_CBC, IV=b'\0\0\0\0\0\0\0\0')
    return cipher.encrypt(order.encode().ljust(16, b'\0'))


# #####################################
# Payment form
# #####################################

def pay(amount, order):

    # Transaction data
    data['DS_MERCHANT_ORDER']  = str(order)
    data['DS_MERCHANT_AMOUNT'] = str(amount)
    data['DS_MERCHANT_URLOK']  = MERCHANT_URLOK + str(order)
    data['DS_MERCHANT_URLKO']  = MERCHANT_URLKO + str(order)

    # Merchant parameters
    text = json.dumps(data).replace(' ', '').replace('\n', '')
    params = base64.b64encode(text.encode('utf-8'))
    print(params.decode('utf-8'))

    # Diversify key
    secret_key: bytes = MERCHANT_KEY.encode()
    cipher = DES3.new(base64.b64decode(secret_key), DES3.MODE_CBC, IV=b'\0\0\0\0\0\0\0\0')
    key = cipher.encrypt(order.encode().ljust(16, b'\0'))

    # Signature
    signature = base64.b64encode(hmac.new(key, params, hashlib.sha256).digest())
    print(signature.decode())

    return '''
    <html>
    <form name="from" action="https://sis-t.redsys.es:25443/sis/realizarPago" method="POST">
    <input type="hidden" name="Ds_SignatureVersion" value="HMAC_SHA256_V1"/>
    <input type="hidden" name="Ds_MerchantParameters" value="{}"/>
    <input type="hidden" name="Ds_Signature" value="{}"/>
    <input type="submit">
    </form>
    </html>
    '''.format(params.decode(), signature.decode())