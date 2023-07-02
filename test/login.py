from flask import Flask, request, make_response, send_file
from datetime import timedelta
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
import secrets
import base64
import json

app = Flask(__name__)

KEY = b'COTOWN-WEB-COTOWN-WEB-COTOWN-WEX'

def encrypt(ptext, nonce):

  try:
    cipher = Cipher(algorithms.ChaCha20(KEY, nonce), mode=None)
    encryptor = cipher.encryptor()
    return encryptor.update(ptext.encode()) + encryptor.finalize()
  except:
    return None


def decrypt(ctext, nonce):

  try:
    cipher = Cipher(algorithms.ChaCha20(KEY, nonce), mode=None)
    decryptor = cipher.decryptor()
    return decryptor.update(ctext) + decryptor.finalize()
  except:
    return None
  

def get_user():

  # Get and decypher cookie
  cookie = request.cookies.get('user')
  if cookie:
    try:
      cookie = json.loads(base64.b64decode(cookie).decode('utf-8'))
      return json.loads(decrypt(base64.b64decode(cookie['credentials']), base64.b64decode(cookie['nonce'])))
    except:
      return None


@app.route('/')
def form():
  
  # Cookie
  print(get_user()) 

  # Login form
  return send_file('login.html', mimetype='text/html')


@app.route('/logout', methods=['POST'])
def logout():

  response = make_response(send_file('login.html'))
  response.set_cookie('user', '', max_age=0)
  return response


@app.route('/login', methods=['POST'])
def login():

  # Cookie
  print(get_user())

  # Get login data
  usr = request.form.get('usr')
  pwd = request.form.get('pwd')

  # Cypher credentials
  nonce = secrets.token_bytes(16)
  creds = json.dumps({ 'usr': usr, 'pwd': pwd, 'token': 'TOKENXXX' })
  ctext = encrypt(creds, nonce)

  # Set cookie
  cookie = {
    'name': 'Alejandro',
    'credentials': base64.b64encode(ctext).decode('utf-8'),
    'nonce': base64.b64encode(nonce).decode('utf-8')
  }
  response = make_response(send_file('login.html'))
  response.set_cookie('user', base64.b64encode(json.dumps(cookie).encode()).decode('utf-8'), max_age=timedelta(days=60))
  return response


if __name__ == '__main__':
    
  app.run(host='0.0.0.0', port=5000, debug=True)
