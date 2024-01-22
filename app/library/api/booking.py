# ###################################################
# API REST
# ---------------------------------------------------
# API for dynamic web (booking)
# ###################################################

# ###################################################
# Imports
# ###################################################

# System includes
import locale
from flask import g, request, session, send_from_directory

# Cotown includes - services
from library.services.config import settings
from library.services.ac import add_contact

# Cotown includes - business functions
from library.business.send_email import smtp_mail
from library.business.booking import *

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Auxiliary methods
# ###################################################

# ---------------------------------------------------
# Jinja2 filters
# ---------------------------------------------------

def format_number(value):
  return locale.format_string("%d", value, grouping=True)

def format_date_es(value):
  return value[8:10] + '/' + value[5:7] + '/' + value[0:4]

def format_date_en(value):
  return value[5:7] + '/' + value[8:10] + '/' + value[0:4]

# ---------------------------------------------------
# Get int or 0
# ---------------------------------------------------

def to_int(value):

  try:
    return int(value)
  except:
    return 0
  
# ---------------------------------------------------
# Process DB errors
# ---------------------------------------------------

def process_error(msg):

  parts = msg.split('!!!')
  if len(parts) > 2:
    return { 'en': parts[1], 'es': parts[2] }
  return msg
  
# ---------------------------------------------------
# Get variable from form, request or session
# ---------------------------------------------------

def get_var(name, default=None, save=True):

    # Get var from querystring
    aux = request.args.get(name)

    # Or get var from form
    if aux is None:
      aux = request.form.get(name)

    # Not session var
    if not save:
      return aux

    # And store in session
    if aux is not None:
      session[name] = aux

    # Or store default value in session
    if name not in session:
      session[name] = default

    # Get value from session
    return session[name]


# ###################################################
# Static web
# ###################################################

# ---------------------------------------------------
# Handles forms posts from web
# ---------------------------------------------------

def req_form():

    # Get form fields
    contact = {}
    for item in request.form:
      contact[item] = request.form.get(item)

    # Attachment?
    file = None
    if 'file' in request.files:
      file = request.files['file']
      if file.filename == '':
        file = None

    # Add contact
    listid = contact.get('listid', None)
    id = str(add_contact(contact, listid))

    # Prepare and send email
    forms = {
      "27": "Disponibilidad",
      "28": "Visita",
      "29": "Contacto",
      "30": "Ventajas",
      "31": "Equipo"
    }
    fields = {
      "email": "Email",
      "firstName": "Nombre",
      "lastName": "Apellidos",
      "phone": "Teléfono",
      "1": "Edad",
      "3": "Nacionalidad",
      "27": "Empresa",
      "95": "Presupuesto",
      "96": "Desde",
      "97": "Hasta",
      "98": "Motivo",
      "99": "Tipo de plaza",
      "100": "Edificio",
      "101": "Ciudad",
      "180": "Fecha visita",
      "181": "Mensaje"
    }
    message = '<h2>' + contact['186'] + '</h2><h3>Formulario: ' + forms[str(listid)] + '</h3>'
    for item in contact:
      if fields.get(item):
        message = message + '<li><b>' + fields[item] + '</b>: ' + contact[item] + '</li>'
    smtp_mail(settings.EMAIL_TO, 'Formulario ' + forms[str(listid)], message, file=file)

    # Return contact ID
    return id


# ###################################################
# Security endpoints
# ###################################################

# ---------------------------------------------------
# Web login
# ---------------------------------------------------

def login(usr, pwd):

    # Call backend
    g.apiClient.auth(user=usr, password=pwd)
    if g.apiClient.token is None:
      return None, None

    # Get user name
    result = g.apiClient.call(
    '''{ 
      data: Customer_CustomerList (
        orderBy: [{ attribute: id }] 
        limit:2
      ) { 
        id
        Name 
        Email
        Phones
        Birth_date
        Nationality_id
        Gender_id
      } 
    }''')
    if len(result['data']) != 1:
      return None, None

    # Ok!
    customer = result['data'][0]
    customer['Prefix'] = customer['Phones'].strip().split(' ')[0]
    customer['Phone'] = ' '.join(customer['Phones'].strip().split(' ')[1:])
    return g.apiClient.token, customer

# ---------------------------------------------------
# Web register
# ---------------------------------------------------

def register():

  # Insert customer
  customer = {   
   'Name': get_var('Name', save=False),
   'Email': get_var('Email', save=False),
   'Prefix': get_var('Prefix', save=False),
   'Phone': get_var('Phone', save=False),
   'Phones': get_var('Prefix', save=False) + ' ' + get_var('Phone', save=False),
   'Birth_date': get_var('Birth_date', save=False) ,
   'Nationality_id': to_int(get_var('Nationality_id', save=False)),
   'Gender_id': to_int(get_var('Gender_id', save=False)) 
  }
  id, error = q_insert_customer(g.dbClient, customer)

  # Error?
  if error:
    if error.pgcode == '23505':
      return None, customer, { 'en': 'Email already exists', 'es': 'El Email ya existe!!!' }
    return None, customer, process_error(error.pgerror)
  
  # Login current created user
  customer['id'] = id
  logged, customer = login(customer['Email'], 'Passw0rd!')
  return logged, customer, None


# ######################################################
# Booking process
# ######################################################

# ---------------------------------------------------
# Get types
# ---------------------------------------------------

def req_typologies(segment):

    return q_typologies(g.dbClient, segment)

# ---------------------------------------------------
# Retrieve assets (CSS, JS) for testing purposes only
# ---------------------------------------------------

def req_pub_asset(filename):

    # Debug
    logger.info('ASSET ' + filename)

    # return
    return send_from_directory('assets', filename)

# ---------------------------------------------------
# Booking process
# ---------------------------------------------------

def req_pub_availability(type, filter):

  date_from = get_var('date_from')
  date_to   = get_var('date_to')
  result = q_availability(g.dbClient, type, filter, date_from, date_to)
  return result

# ---------------------------------------------------
# Booking process
# ---------------------------------------------------

def req_pub_booking(step):

    # Examples
    #
    # http://localhost:5000/booking/2?lang=en&segment=1&book_city_id=1&book_acom=pc&book_room=ind&book_checkin=2024-05-01&book_checkout=2024-07-31
    # http://localhost:5000/booking/3?lang=en&segment=1&book_building_id=1&book_flat_type_id=1&book_place_type_id=100&book_checkin=2024-05-01&book_checkout=2024-07-31
    #
    # http://localhost:5000/booking/2?lang=en&segment=1&book_city_id=1&book_acom=ap&book_checkin=2024-05-01&book_checkout=2024-07-31
    # http://localhost:5000/booking/3?lang=en&segment=1&book_building_id=1&book_flat_type_id=5&book_place_type_id=1&book_acom=ap&book_checkin=2024-05-01&book_checkout=2024-07-31

    # Debug
    logger.info('BOOKING STEP-' + str(step) + ':' + request.path)
    error_book = None
    error_login = None
    error_register = None

    # Common data: step, language and segment
    step    = int(step)
    action  = get_var('book_action')
    lang    = get_var('lang', 'es')
    segment = get_var('segment', 1)

    # Locale
    locale.setlocale(locale.LC_ALL, 'es_ES' if lang == 'es' else 'en_US')

    # Booking data from each step
    typologies    = q_typologies(g.dbClient, segment)
    city_id       = int(get_var('book_city_id', 1)) 
    city          = [dic for dic in typologies if dic.get('id') == city_id][0]
    acom_type     = get_var('book_acom')
    room_type     = get_var('book_room')
    date_from     = get_var('book_checkin')
    date_to       = get_var('book_checkout') 
    building_id   = get_var('book_building_id')
    place_type_id = get_var('book_place_type_id')
    flat_type_id  = get_var('book_flat_type_id')
    extras        = get_var('book_extras')
    booking_id    = 0

    # Current user, if logged
    logged   = session.get('logged', None)
    customer = session.get('customer', None)

    # ---------------------------------------------------
    # STEP 1
    # ---------------------------------------------------
    if step == 1:

      # Get existing locations, types, etc.
      pass

    # ---------------------------------------------------
    # STEP 2
    # ---------------------------------------------------
    elif step == 2:

      # Search results
      results = q_book_search(g.dbClient, segment, lang, date_from, date_to, city_id, acom_type, room_type)
    
    # ---------------------------------------------------
    # STEP 3
    # ---------------------------------------------------
    elif step == 3:

      # Show summary
      genders   = q_genders(g.dbClient, lang)
      reasons   = q_reasons(g.dbClient, lang)
      countries = q_countries(g.dbClient, lang)
      summary   = q_book_summary(g.dbClient, lang, date_from, date_to, building_id, place_type_id, flat_type_id, acom_type)
      
    # ---------------------------------------------------
    # STEP 4 - Logout
    # ---------------------------------------------------
    elif step == 4 and action == 'logout':

      # Log out
      logged = None
      session['logged'] = logged
      session['customer'] = None
      step = 3

      # Show summary again
      genders   = q_genders(g.dbClient, lang)
      reasons   = q_reasons(g.dbClient, lang)
      countries = q_countries(g.dbClient, lang)
      summary   = q_book_summary(g.dbClient, lang, date_from, date_to, building_id, place_type_id, flat_type_id, acom_type)

    # ---------------------------------------------------
    # STEP 4 - Login
    # ---------------------------------------------------
    elif step == 4 and action == 'login':

      # Data from step 4/login (or session)
      user = get_var('book_user')
      pswd = get_var('book_password')

      # Try to log in 
      logged, customer = login(user, pswd)
      session['logged'] = logged
      session['customer'] = customer
      if logged is None:
        error_login = { 'en': 'Wrong email or password', 'es': 'Email o clave incorrectos' }
      step = 3
    
      # Show summary again
      genders   = q_genders(g.dbClient, lang)
      reasons   = q_reasons(g.dbClient, lang)
      countries = q_countries(g.dbClient, lang)
      summary   = q_book_summary(g.dbClient, lang, date_from, date_to, building_id, place_type_id, flat_type_id, acom_type)

    # ---------------------------------------------------
    # STEP 4 - Register
    # ---------------------------------------------------
    elif step == 4 and action == 'register':
       
      # Try to register
      logged, customer, error_register = register()
      session['logged'] = logged
      session['customer'] = customer
      step = 3
    
      # Show summary again
      genders   = q_genders(g.dbClient, lang)
      reasons   = q_reasons(g.dbClient, lang)
      countries = q_countries(g.dbClient, lang)
      summary   = q_book_summary(g.dbClient, lang, date_from, date_to, building_id, place_type_id, flat_type_id, acom_type)

    # ---------------------------------------------------
    # STEP 4 - Book
    # ---------------------------------------------------

    elif step == 4 and action == 'book':

      # Try to mke the reservation book
      summary = q_book_summary(g.dbClient, lang, date_from, date_to, building_id, place_type_id, flat_type_id, acom_type)
      booking = {
        'Date_from': date_from,
        'Date_to': date_to,
        'Customer_id': customer['id'],
        'Building_id': building_id,
        'Resource_type': 'piso' if acom_type == 'ap' else 'habitacion',
        'Flat_type_id': place_type_id if acom_type == 'ap' else flat_type_id,
        'Place_type_id': None if acom_type == 'ap' else place_type_id,
        'Reason_id': get_var('Reason_id', None),
        'Comments': summary['Building_name'] + ' / ' + summary['Place_type_name'] + ' / ' + summary['Flat_type_name'] + (' / ' + extras) if extras else ''
      }
      booking_id, error = q_insert_booking(g.dbClient, booking)

      # Error?
      if error:
        return None, customer, error # process_error(error.pgerror) 

    # Add your custom filter to Jinja2 environment
    g.env.filters['number'] = format_number
    g.env.filters['date']   = format_date_es if lang == 'es' else format_date_en
    tpl = g.env.get_template(lang + '/step-' + str(step) + '.html')
    return tpl.render(data=locals())