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

MERCHANT_CURRENCY        = '978'       # Euro
MERCHANT_MERCHANTCODE    = '348032921' # Test
MERCHANT_TERMINAL        = '002'       # Terminal 1
MERCHANT_TRANSACTION_PAY = '0'         # Pago
MERCHANT_KEY             = 'sq7HjrUOBfKmC576ILgskD5srU870gJ7'


# #####################################
# 3DES cypher
# # #####################################

def encrypt_DES3(order: str) -> bytes:

    secret_key: bytes = MERCHANT_KEY.encode('utf-8')
    key = base64.b64decode(secret_key)
    cipher = DES3.new(key, DES3.MODE_CBC, IV=b'\0\0\0\0\0\0\0\0')
    return cipher.encrypt(order.encode('utf-8').ljust(16, b'\0'))


def calc_signature(order, params):

    # Diversify key
    secret_key: bytes = MERCHANT_KEY.encode('utf-8')
    cipher = DES3.new(base64.b64decode(secret_key), DES3.MODE_CBC, IV=b'\0\0\0\0\0\0\0\0')
    key = cipher.encrypt(order.encode('utf-8').ljust(16, b'\0'))

    # Signature
    signature = base64.b64encode(hmac.new(key, params, hashlib.sha256).digest())
    return signature


# #####################################
# Payment form
# #####################################

def pay(server, amount, order):

    # Transaction data
    data = {
        'DS_MERCHANT_CURRENCY'       : MERCHANT_CURRENCY,
        'DS_MERCHANT_MERCHANTCODE'   : MERCHANT_MERCHANTCODE,
        'DS_MERCHANT_TERMINAL'       : MERCHANT_TERMINAL,
        'DS_MERCHANT_TRANSACTIONTYPE': MERCHANT_TRANSACTION_PAY,
        'DS_MERCHANT_URLOK'          : 'https://' + server + '/ok?op=' + str(order),
        'DS_MERCHANT_URLKO'          : 'https://' + server + '/ko?op=' + str(order),
        'DS_MERCHANT_MERCHANTURL'    : 'https://' + server + '/notify',
        'DS_MERCHANT_ORDER'          : str(order),
        'DS_MERCHANT_AMOUNT'         : str(amount)
    }

    # Merchant parameters
    text = json.dumps(data).replace(' ', '').replace('\n', '')
    params = base64.b64encode(text.encode('utf-8'))
    print(data, flush=True)
    print(params.decode('utf-8'), flush=True)

    # Signature
    signature = calc_signature(order, params)
    print(signature.decode('utf-8'), flush=True)

    return '''
    <html>
    <form name="from" action="https://sis-t.redsys.es:25443/sis/realizarPago" method="POST" target="_top">
    <input type="hidden" name="Ds_SignatureVersion" value="HMAC_SHA256_V1"/>
    <input type="hidden" name="Ds_MerchantParameters" value="{}"/>
    <input type="hidden" name="Ds_Signature" value="{}"/>
    <input type="submit">
    </form>
    </html>
    '''.format(params.decode('utf-8'), signature.decode('utf-8'))


# #####################################
# Validate payment
# #####################################

def validate(response):

    # Received params
    params = response['Ds_MerchantParameters']
    print(params, flush=True)

    # Get DS_ORDER
    result = json.loads(base64.b64decode(params).decode('utf-8'))
    print(result, flush=True)

    # Calc signatures
    calculated_signature = calc_signature(result['Ds_Order'], params.encode('utf-8')).decode('utf-8')
    received_signature = response['Ds_Signature'].replace('_', '/').replace('-', '+')
    print(calculated_signature, flush=True)
    print(received_signature, flush=True)
    
    # Check signature
    if calculated_signature != received_signature:
        print('Dont match')
        return None
    
    # Return response
    return result
