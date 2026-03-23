# ###################################################
# API REST
# ---------------------------------------------------
# Miscelaneous functions
# ###################################################

# ###################################################
# Imports
# ###################################################
 
# System includes
import re
import json
import base64
import hashlib
from flask import g, send_file, abort, Response
from schwifty import IBAN, exceptions
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from datetime import datetime, timedelta, timezone
from io import BytesIO
from icalendar import Calendar, Event

# Cotown includes
from library.services.config import settings
from library.services.apiclient import APIClient
from library.services.utils import flatten
from library.business.contract import BOOKING, month, decimal
from library.business.queries import q_change_contract

# Logging
import logging
logger = logging.getLogger('COTOWN')


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
  regex = '^[A-Z]{4}[-]{0,1}[A-Z]{2}[-]{0,1}[A-Z0-9]{2}[-]{0,1}([0-9]{3})?$'
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


# iCAL URL
def req_ical(token):

  #?print(token)
  #?token = generate_token('BLM335.01.01', 'COTOWN')
  #?print(token)

  # DBClient   
  dbClient = g.dbClient

  # Token
  code = decode_token(token, 'COTOWN')
  print(code)

  # Query
  sql = '''
  SELECT
    r."Code",
    bd."Date_from",
    bd."Date_to"
  FROM "Booking"."Booking_detail" bd
  JOIN "Resource"."Resource" r ON r.id = bd."Resource_id"
  WHERE r."Code" = %s
    AND bd."Date_to" >= CURRENT_DATE
  ORDER BY bd."Date_from"
  '''
    
  # Retrieve data
  try:
    con = dbClient.getconn()
    cur = dbClient.execute(con, sql, (code,))
    rows = cur.fetchall()
    cur.close()
    dbClient.putconn(con)
  except Exception as error:
    logger.error(error)
    con.rollback()
    dbClient.putconn(con)
    return None

  # Create feed
  cal = Calendar()
  cal.add("prodid", "-//booking//ical//")
  cal.add("version", "2.0")
  for resource, date_from, date_to in rows:
    event = Event()
    event.add("uid", f"{resource}@recurso")
    event.add("summary", f"Reserva {resource}")
    event.add("dtstart", date_from)
    event.add("dtend", date_to + timedelta(days=1))
    event.add("dtstamp", datetime.now(timezone.utc))
    cal.add_component(event)

  return Response(
    cal.to_ical(),
    headers={
      "Content-Type": "text/calendar; charset=utf-8",
      "Content-Disposition": f'inline; filename="{code}.ics"'
    }
  )