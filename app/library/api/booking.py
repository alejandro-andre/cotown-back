# ###################################################
# API REST
# ---------------------------------------------------
# API for dynamic web (booking)
# ###################################################

# ###################################################
# Imports
# ###################################################

# System includes
from flask import g, request, session, abort, make_response, send_file, send_from_directory
from datetime import timedelta
import base64
import json

# Cotown includes - services
from library.services.cipher import encrypt
from library.services.config import settings
from library.services.ac import add_contact

# Cotown includes - business functions
from library.business.send_email import smtp_mail
from library.business.booking import q_typologies, q_book_search, q_book_summary, q_insert_customer, q_genders, q_reasons, q_countries

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Auxiliary methods
# ###################################################

# ---------------------------------------------------
# Get variable from form, request or session
# ---------------------------------------------------

def get_var(name, default=None):

    # Get var from querystring
    aux = request.args.get(name)

    # Or get var from form
    if aux is None:
      aux = request.form.get(name)

    # And store in session
    if aux is not None:
      session[name] = aux

    # Or store default value in session
    if name not in session:
      session[name] = default

    # Get value from session
    return session[name]

# ---------------------------------------------------
# Insert a new customer
# ---------------------------------------------------

def insert_customer(name, email):
  
   customer_id = q_insert_customer(g.dbClient, name, email)
   return customer_id
  

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
    listid = contact['listid']
    if listid:
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
    message = '<h2>vanguard-student-housing-com</h2><h3>Formulario: ' + forms[str(listid)] + '</h3>'
    for item in contact:
      if fields.get(item):
        message = message + '<li><b>' + fields[item] + '</b>: ' + contact[item] + '</li>'
    smtp_mail(settings.EMAIL_TO, 'Formulario ' + forms[str(listid)], message, file=file)

    # Return contact ID
    return


# ###################################################
# Security endpoints
# ###################################################

# ---------------------------------------------------
# Web logout
# ---------------------------------------------------

def req_logout():

    response = make_response(send_file('static/login.html'))
    response.set_cookie('user', '', max_age=0)
    return response


# ---------------------------------------------------
# Web login
# ---------------------------------------------------

def login(usr, pwd):

    # Call backend
    print(usr, pwd)
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
    customer['Prefix'] = customer['Phones'].split(' ')[0]
    customer['Phones'] = ''.join(customer['Phones'].split(' ')[1:])
    return g.apiClient.token, customer


# ---------------------------------------------------
# Web register
# ---------------------------------------------------

def req_register():
   
   return 'ok'


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

def req_pub_booking(step):

    # Debug
    logger.info('BOOKING STEP-' + str(step) + ':' + request.path)

    # Common data: step, language and segment
    data     = {}
    error    = None      
    step     = int(step)
    lang     = get_var('lang', 'es')
    segment  = get_var('segment', 1)

    # Current user, if logged
    logged   = session.get('logged', None)
    customer = session.get('customer', None)

    # Get info
    types = q_typologies(g.dbClient, segment)

    # http://localhost:5000/booking/2?lang=en&segment=1&book_city_id=1&book_acom=pc&book_room=ind&book_checkin=2023-11-01&book_checkout=2024-03-31

    # Data from step 2 (or session)
    acom_type     = get_var('book_acom')
    room_type     = get_var('book_room')
    date_from     = get_var('book_checkin')
    date_to       = get_var('book_checkout')
    city_id       = int(get_var('book_city_id', 1))
    city          = [dic for dic in types if dic.get('id') == city_id][0]

    # Data from step 3 (or session)
    building_id   = get_var('book_building_id')
    place_type_id = get_var('book_place_type_id')
    flat_type_id  = get_var('book_flat_type_id')

    # Data from step 4/login (or session)
    action        = get_var('book_action')
    user          = get_var('book_user')
    pswd          = get_var('book_password')

    # ---------------------------------------------------
    # STEP 1
    # ---------------------------------------------------
    if step == 1:

      # Get existing locations, types, etc.
      typologies = types  

    # ---------------------------------------------------
    # STEP 2
    # ---------------------------------------------------
    elif step == 2:

      # Search results
      results    = q_book_search(g.dbClient, segment, lang, date_from, date_to, city_id, acom_type, room_type)
    
    # ---------------------------------------------------
    # STEP 3
    # ---------------------------------------------------
    elif step == 3:

      # Show summary
      genders    = q_genders(g.dbClient, lang)
      reasons    = q_reasons(g.dbClient, lang)
      countries  = q_countries(g.dbClient, lang)
      summary    = q_book_summary(g.dbClient, lang, date_from, date_to, building_id, place_type_id, flat_type_id, acom_type)

    # ---------------------------------------------------
    # STEP 4 - Login
    # ---------------------------------------------------
    elif step == 4 and action == 'login':

      # Try to log in 
      logged, customer = login(user, pswd)
      session['logged'] = logged
      session['customer'] = customer
      if logged is None:
        error = 'Email o clave incorrectos'
      else:
        error = None
      step = 3
    
      # Show summary again
      genders    = q_genders(g.dbClient, lang)
      reasons    = q_reasons(g.dbClient, lang)
      countries  = q_countries(g.dbClient, lang)
      summary    = q_book_summary(g.dbClient, lang, date_from, date_to, building_id, place_type_id, flat_type_id, acom_type)

    # ---------------------------------------------------
    # STEP 4 - Register
    # ---------------------------------------------------
    elif step == 4 and action == 'register':
       
      # Try to register
      logged = 'new user'
      session['logged'] = logged
      step = 3
    
      # Show summary again
      genders    = q_genders(g.dbClient, lang)
      reasons    = q_reasons(g.dbClient, lang)
      countries  = q_countries(g.dbClient, lang)
      summary    = q_book_summary(g.dbClient, lang, date_from, date_to, building_id, place_type_id, flat_type_id, acom_type)

    # ---------------------------------------------------
    # STEP 4 - Book
    # ---------------------------------------------------

    elif step == 4 and action == 'book':

      # Try to mke the reservation book
      pass
    
    # Render template
    print(customer)
    tpl = g.env.get_template(lang + '/step-' + str(step) + '.html')
    return tpl.render(data=locals())