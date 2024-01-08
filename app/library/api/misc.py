# ###################################################
# API REST
# ---------------------------------------------------
# Miscelaneous functions
# ###################################################

# ###################################################
# Imports
# ###################################################
 
# System includes
from schwifty import IBAN, exceptions
import re

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Misc functions
# ###################################################

# Hi - I'm live endpoint
def req_pub_hello():

  logger.debug('Hi')
  return 'Hi!'


# Validate IBAN format and content
def req_validate_iban(code):

  # Clean code
  code = re.sub(r'[^a-zA-Z0-9]', '', code)

  # Validate
  try:
    iban = IBAN(code, allow_invalid=False, validate_bban=True)
    return iban
  except exceptions.InvalidLength:
      return '!!!Invalid length!!!Longitud inválida!!!'
  except exceptions.InvalidStructure:
      return '!!!Invalid structure!!!Estructura inválida!!!'
  except exceptions.InvalidChecksumDigits:
      return '!!!Invalid checksum!!!Dígittos de control inválidos!!!'
  except Exception as ex:
      return ex

  
# Validate SWIFT format
def req_validate_swift(code):
   
  # Empty string
  if (str == None):
      return False

  # Clean code  
  code = re.sub(r'[^a-zA-Z0-9]', '', code)

  # Regex to check valid SWIFT Code
  regex = '^[A-Z]{4}[-]{0,1}[A-Z]{2}[-]{0,1}[A-Z0-9]{2}[-]{0,1}[0-9]{3}$'
  return re.search(regex, code)
