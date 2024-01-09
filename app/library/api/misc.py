# ###################################################
# API REST
# ---------------------------------------------------
# Miscelaneous functions
# ###################################################

# ###################################################
# Imports
# ###################################################
 
# System includes
from flask import send_file, abort
from schwifty import IBAN, exceptions
import re

# Cotown includes
from library.services.config import settings
from library.services.apiclient import APIClient
from library.services.utils import flatten
from library.business.print_contract import BOOKING, generate_doc_file

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
  return 'ok' if re.search(regex, code) else 'ko'


# Residence certificate
def req_cert_booking(booking):

  # API Client   
  apiClient = APIClient(settings.SERVER)
  apiClient.auth(user=settings.GQLUSER, password=settings.GQLPASS)

  # Get template
  q = '''{
    data: Provider_Provider_contractList ( where: { Name: { EQ: "Certificado de residencia" } } ) {
      Name
      Template
    }
  }
  '''
  result = apiClient.call(q)
  template = result['data'][0]['Template']
  
  # Get booking
  booking = apiClient.call(BOOKING, { "id": booking })
  if booking is None:
    abort(404)

  # Prepare booking
  context = flatten(booking['data'][0])

  # Generate rent contract
  file = generate_doc_file(context, template)
  return send_file(file, mimetype='application/pdf')