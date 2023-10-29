from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
import secrets

KEY = b'COTOWN-WEB-COTOWN-WEB-COTOWN-WEB'

def encrypt(ptext):

 nonce = secrets.token_bytes(16)

 try:
   cipher = Cipher(algorithms.ChaCha20(KEY, nonce), mode=None)
   encryptor = cipher.encryptor()
   return encryptor.update(ptext.encode()) + encryptor.finalize(), nonce
 except:
   return None, None


def decrypt(ctext, nonce):

 try:
   cipher = Cipher(algorithms.ChaCha20(KEY, nonce), mode=None)
   decryptor = cipher.decryptor()
   return decryptor.update(ctext) + decryptor.finalize()
 except:
   return None
 

