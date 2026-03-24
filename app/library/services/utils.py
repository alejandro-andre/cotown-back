# ######################################################
# Imports
# ######################################################

import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


# ######################################################
# Flatten JSON
# ######################################################

def super_flatten(data, prefix=''):
   
    flattened = {}

    # Dictionaries
    if isinstance(data, dict):
      for key, value in data.items():
        new_key = f"{prefix}{key}"
        if isinstance(value, (dict, list)):
          flattened.update(super_flatten(value, prefix=f"{new_key}."))
        else:
          flattened[new_key] = value

    # Lists
    elif isinstance(data, list):
      for i, item in enumerate(data):
        new_key = f"{prefix}{i}"
        if isinstance(item, (dict, list)):
          flattened.update(super_flatten(item, prefix=f"{new_key}."))
        else:
          flattened[new_key] = item

    else:
      flattened[prefix] = data

    return flattened


def flatten(json_obj, key='', flattened=None, prefix=''):

  # Empty json, create empty result
  if flattened is None:
    flattened = {}

  # Dictionary, get every key, and flatten each item
  if isinstance(json_obj, dict):
    for key, value in json_obj.items():
      new_prefix = f"{prefix}.{key}" if prefix else key
      flatten(value, key, flattened, new_prefix)

  # List, keep the list flattening each element
  elif isinstance(json_obj, list):
    array = []
    for i, value in enumerate(json_obj):
      array.append(flatten(value))
    flattened[key] = array

  # Scalar, store item
  else:
    if json_obj is None:
      flattened[key] = ''
    else:
      flattened[key] = json_obj

  return flattened


# ###################################################
# Crypto functions
# ###################################################

def _normalize_key(secret: str) -> bytes:
    return hashlib.sha256(secret.encode("utf-8")).digest()

def generate_token(code: str, secret: str) -> str:
    key = _normalize_key(secret)
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(code.encode("utf-8"))
    return base64.urlsafe_b64encode(cipher.nonce + tag + ciphertext).decode("utf-8")

def decode_token(token: str, secret: str) -> str:
    key = _normalize_key(secret)
    raw = base64.urlsafe_b64decode(token.encode("utf-8"))
    nonce = raw[:16]
    tag = raw[16:32]
    ciphertext = raw[32:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode("utf-8")