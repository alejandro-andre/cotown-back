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
from flask import g, send_file, abort, Response
from schwifty import IBAN, exceptions
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML
from datetime import date, datetime, timedelta, timezone
from io import BytesIO
from icalendar import Calendar, Event
from zoneinfo import ZoneInfo

# Cotown includes
from library.services.config import settings
from library.services.apiclient import APIClient
from library.services.utils import flatten, generate_token, decode_token
from library.business.contract import BOOKING, month, decimal
from library.business.queries import q_change_contract

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

  # DBClient
  dbClient = g.dbClient

  # Query
  sql = '''
    SELECT
      r."Code",
      bd.id,
      bd."Date_from",
      bd."Date_to"
    FROM "Resource"."Resource" r
      LEFT JOIN "Booking"."Booking_detail" bd  ON r.id = bd."Resource_id" AND bd."Date_to" >= CURRENT_DATE
    WHERE r."Ical" = %s
    ORDER BY bd."Date_from"
  '''

  # Retrieve data
  logger.debug(token)
  code = 'unknown'
  try:
    con = dbClient.getconn()
    cur = dbClient.execute(con, sql, ('https://back.cotown.com/api/v1/ical/' + token,))
    rows = cur.fetchall()
    cur.close()
    dbClient.putconn(con)
  except Exception as error:
    logger.error(error)
    if con:
      con.rollback()
      dbClient.putconn(con)
    return None

  # Sin resultados = recurso no existe
  if not rows:
    abort(404)

  # Calculate current weekend
  madrid = ZoneInfo("Europe/Madrid")
  now_madrid = datetime.now(madrid)
  today = now_madrid.date()
  monday = today - timedelta(days=today.weekday())
  current_weekend = [monday + timedelta(days=i) for i in (4, 5, 6)]

  def is_day_booked(day, booked_ranges):
    return any(date_from <= day <= date_to for date_from, date_to in booked_ranges)

  # Create feed
  cal = Calendar()
  cal.add("prodid", "-//booking//ical//")
  cal.add("version", "2.0")
  booked_ranges = []
  now = datetime.now(timezone.utc)
  for resource, id, date_from, date_to in rows:
    code = resource
    logger.debug("{} {} {} {}".format(resource, id, date_from, date_to))
    if date_from:
      booked_ranges.append((date_from, date_to))
      event = Event()
      event.add("uid", f"{id}@{resource}")
      event.add("summary", f"Reserva {resource}-{id}")
      event.add("dtstart", date_from)
      event.add("dtend", date_to + timedelta(days=1))
      event.add("dtstamp", now)
      cal.add_component(event)

  # Block weekend days only from Friday 12:00 (Madrid time) onwards
  friday, saturday, sunday = current_weekend

  is_blocking_period = (
    (today == friday and now_madrid.hour >= 10) or
    today == saturday or
    today == sunday
  )

  if is_blocking_period:
    for day in [friday, saturday, sunday]:
      if not is_day_booked(day, booked_ranges):
        event = Event()
        event.add("uid", f"N{day.isoformat()}@{code}")
        event.add("summary", f"No disponible {code}")
        event.add("dtstart", day)
        event.add("dtend", day + timedelta(days=1))
        event.add("dtstamp", now)
        cal.add_component(event)

  return Response(
    cal.to_ical(),
    headers={
      "Content-Type": "text/calendar; charset=utf-8",
      "Content-Disposition": f'inline; filename="{code}.ics"'
    }
  )