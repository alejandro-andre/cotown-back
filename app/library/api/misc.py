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
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML
from datetime import datetime
from io import BytesIO
import re

# Cotown includes
from library.services.config import settings
from library.services.apiclient import APIClient
from library.services.utils import flatten
from library.business.print_contract import BOOKING, month, decimal

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

  # Jinja environment
  env = Environment(
    loader=FileSystemLoader('./templates/other'),
    autoescape=select_autoescape(['html', 'xml'])
  )
  env.filters['decimal'] = decimal
  env.filters['month'] = month

  # Get booking
  booking = apiClient.call(BOOKING, { "id": booking })
  if booking is None:
    abort(404)

  # Prepare booking
  context = flatten(booking['data'][0])
  now = datetime.now()
  context['Today_day'] = now.day
  context['Today_month'] = now.month
  context['Today_year'] = now.year
  context['Server'] = 'https://' + settings.BACK + settings.API_PREFIX

  # Generate HTML
  tpl = env.get_template('cert.html')
  result = tpl.render(context)

  # Generate PDF
  file = BytesIO()
  html = HTML(string=result)
  html.write_pdf(file)
  file.seek(0)
  return send_file(file, mimetype='application/pdf')