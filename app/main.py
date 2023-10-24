# ###################################################
# API REST
# ---------------------------------------------------
# Business back office logic for Cotown
# ###################################################

# #####################################
# Imports
# #####################################

# System includes
from flask import Flask, request, abort, make_response, send_file, send_from_directory, render_template
from jinja2 import Environment, FileSystemLoader, select_autoescape
from cachetools import TTLCache
from datetime import timedelta
from io import BytesIO
import base64

# Cotown includes - services
from library.services.dbclient import DBClient
from library.services.apiclient import APIClient
from library.services.cipher import encrypt, decrypt
from library.services.config import settings
from library.services.redsys import pay, validate
from library.services.ac import add_contact

# Cotown includes - business functions
from library.business.export import query_to_excel
from library.business.occupancy import occupancy
from library.business.download import download
from library.business.send_email import smtp_mail
from library.business.queries import *
from library.business.booking import *

# Logging
import logging
logger = logging.getLogger('COTOWN')


# #####################################
# Flask app
# #####################################

def runapp():

  # ###################################################
  # Logging
  # ###################################################

  logger.setLevel(settings.LOGLEVEL)
  console_handler = logging.StreamHandler()
  console_handler.setLevel(settings.LOGLEVEL)
  formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(module)s] [%(funcName)s/%(lineno)d] [%(levelname)s] %(message)s')
  console_handler.setFormatter(formatter)
  logger.addHandler(console_handler)
  logger.info('Started')


  # ###################################################
  # GraphQL and DB client
  # ###################################################

  # graphQL API
  apiClient = APIClient(settings.SERVER)

  # DB API
  dbClient = DBClient(
    host=settings.SERVER, 
    dbname=settings.DATABASE, 
    user=settings.DBUSER, 
    password=settings.DBPASS,
    sshuser=settings.SSHUSER, 
    sshpassword=settings.get('SSHPASS', None),
    sshprivatekey=settings.get('SSHPKEY', None)
  )


  # #####################################
  # Cache
  # #####################################

  cache = TTLCache(maxsize=100, ttl=60)


  # #####################################
  # Templating
  # #####################################

  env = Environment(
    loader=FileSystemLoader('./booking'),
    autoescape=select_autoescape(['html', 'xml'])
  )

  # #####################################
  # Validate token
  # #####################################

  def validate_token(token):

    # Check cache first
    if token in cache:
        return cache[token]

    # Forbidden by default
    result = 403

    # Call API to check if token is valid
    if token is not None:
      try:
        apiClient.auth(token)
        data = apiClient.call('{ user: getCurrentUser { currentUser } }')
        if data['user']['currentUser'] != 'anonymous':
          result = 0
      except:
        pass
      cache[token] = result
      return result

    # Debug / Remove in production
    apiClient.auth(user=settings.GQLUSER, password=settings.GQLPASS)
    logger.warning('Acceso sin token')
    result = 0

    # Forbidden
    return result


  # ###################################################
  # Misc functions
  # ###################################################

  # Hi - I'm live endpoint
  def get_hello():

    logger.debug('Hi')
    return 'Hi!'

  # ###################################################
  # Airflows plugins
  # ###################################################

  # Signature - Returns the signature image
  def get_signature(id):

    # Debug
    logger.debug('Signature ' + str(id))

    # Return image
    image = apiClient.getFile(id, 'Provider/Provider_contact', 'Signature')
    response = send_file(BytesIO(image.content), mimetype=image.headers['content-type'])
    return response

  # Download files (PDFs) in ZIP format - Contracts, bills...
  def get_download(name):

    # Debug
    logger.debug('Download ' + name)

    # Querystring variables
    vars = {}
    for item in dict(request.args).keys():
      try:
        vars[item] = int(request.args[item])
      except:
        vars[item] = request.args[item]
  
    # Download zip
    result = download(apiClient, name, vars)
    if result is None:
      abort(404)

    # Response
    response = send_file(result, mimetype='application/zip')
    response.headers['Content-Disposition'] = 'inline; filename="' + name + '.zip"'
    return response
  
  # Export data (queries) to excel
  def get_export(name):

    # Debug
    logger.debug('Export ' + name)

    # Querystring variables
    vars = {}
    for item in dict(request.args).keys():
      try:
        vars[item] = int(request.args[item])
      except:
        vars[item] = request.args[item]
  
    # Export
    result = query_to_excel(apiClient, dbClient, name, vars)
    if result is None:
      abort(404)

    # Response
    response = send_file(result, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response.headers['Content-Disposition'] = 'inline; filename="' + name + '.xlsx"'
    return response    
        
  # Occupancy report
  def get_occupancy():

    # Querystring variables
    vars = {}
    for item in dict(request.args).keys():
      try:
        vars[item] = int(request.args[item])
      except:
        vars[item] = request.args[item]
  
    result = occupancy(dbClient, vars)
    if result is None:
      abort(404)

    # Response
    response = send_file(result, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response.headers['Content-Disposition'] = 'inline; filename="occupancy.xlsx"'
    return response    

  # Available resources
  def post_availability():
    
    data = request.get_json()
    result = available_resources(
      dbClient, 
      date_from=data.get('date_from'), 
      date_to=data.get('date_to'), 
      building=data.get('building', ''), 
      flat_type=data.get('flat_type', ''),
      place_type=data.get('place_type', '')
    )
    if result is None:
      return {}
    return result
  
  # Change booking status
  def get_booking_status(id, status):

    if booking_status(dbClient, id, status):
      return 'ok'
    return 'ko'
  
  # Dashboard
  def get_dashboard(status = None):

    return dashboard(dbClient, status)

  # Labels
  def get_labels(id, locale):

    return labels(dbClient, id, locale)
  

  # ###################################################
  # Static web
  # ###################################################

  # Forms posts
  def post_form():

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
    return id

  # Get flat types
  def get_flats(year = 2023):
    return flat_prices(dbClient, year)
  
  # Get room types
  def get_rooms(year = 2023):
    return room_prices(dbClient, year)
  
  # Get amenities
  def get_amenities():
    return room_amenities(dbClient)

  # Get types
  def get_types():
    return existing_types(dbClient)


  # ###################################################
  # Dynamic web pages
  # ###################################################

  # Web logout
  def post_logout():

    response = make_response(send_file('static/login.html'))
    response.set_cookie('user', '', max_age=0)
    return response

  # Web login
  def post_login():

    # Response
    response = make_response(send_file('static/login.html'))

    # Get login data
    usr = request.form.get('usr')
    pwd = request.form.get('pwd')

    # Call backend
    apiClient.auth(user=usr, password=pwd)
    if apiClient.token is None:
      return response

    # Get user name
    result = apiClient.call('{ data: Customer_CustomerList (orderBy: [{ attribute: id }] limit:2) { Name } }')
    if len(result['data']) != 1:
      return response

    # Set cookie
    creds = json.dumps({ 'usr': usr, 'pwd': pwd, 'token': apiClient.token })
    ctext, nonce = encrypt(creds)
    cookie = {
      'name': result['data'][0]['Name'],
      'credentials': base64.b64encode(ctext).decode('utf-8'),
      'nonce': base64.b64encode(nonce).decode('utf-8')
    }
    response.set_cookie(
      'user', 
      base64.b64encode(json.dumps(cookie).encode()).decode('utf-8'), 
      max_age=timedelta(days=60),
      domain=".cotown.com"
    )
    return response


  # ###################################################
  # Dynamic web API
  # ###################################################

  # Available typologies for a location between some dates
  def get_available_types():
    
    result = available_types(
      dbClient, 
      date_from=request.args.get('date_from'), 
      date_to=request.args.get('date_to'), 
      location=request.args.get('location', '')
    )
    if result is None:
      return {}
    return result


  # ###################################################
  # Payments
  # ###################################################

  # Prepare payment params
  def get_pay(id):

    # Get payment
    payment = get_payment(dbClient, id, generate_order=True)
    logger.debug(payment)
    logger.debug(payment)
    if payment is None:
      abort(404)
  
    # Redsys data
    params = pay(
      order     = payment['Payment_order'], 
      amount    = int(100 * float(payment['Amount'])), 
      id        = payment['id'],
      urlok     = 'https://' + settings.BACK + '/customer/#/pago_ok?id=' + payment['Payment_order'],
      urlko     = 'https://' + settings.BACK + '/customer/#/pago_ko?id=' + payment['Payment_order'],
    )
    logger.debug(params)

    # Return both information
    return payment | params 
  
  # Notification
  def post_notification():

    # Validate response
    response = validate(request.values)
    if response is None:
      return 'OK'

    # Transaction denied
    if response['Ds_Response'][:2] != '00':
      return 'KO'

    # Get payment
    id = int(response['Ds_MerchantData'])
    payment = get_payment(dbClient, id)
    logger.debug(payment)
    if payment is None:
      return 'KO'

    # Update payment
    date = response['Ds_Date']
    hour = response['Ds_Hour']
    ts = date[6:] + '-' + date[3:5] + '-' + date[:2] + ' ' + hour + ':00'
    logger.debug(ts)
    put_payment(dbClient, id, response['Ds_AuthorisationCode'], ts)

    # Ok
    return 'OK'


  # ###################################################
  # Pages
  # ###################################################

  def get_asset(filename):

    # Debug
    logger.info('ASSET ' + filename)

    # return
    return send_from_directory('assets', filename)

  def get_booking(filename):

    # Debug
    logger.info('BOOKING ' + filename + ':' + request.path)

    # Language
    lang = 'es' if request.path.startswith('es/') else 'en'

    # Get existing locations, types, etc.
    data = {
      'lang': lang,
      'data': existing_types(dbClient) 
    }

    # Render dynamic page
    return env.get_template(filename).render(data=data)


  # ###################################################
  # Flask
  # ###################################################

  # Flask
  app = Flask(__name__)
  
  # Before each request
  @app.before_request
  def before_request():

    # Debug
    logger.info('Recibido ' + request.path)

    # Skip token validaton on public endpoints
    if request.endpoint in ('get_hello', 'post_notification', 'get_asset', 'get_booking'):
      return

    # Token invalid?
    value = validate_token(request.args.get('access_token'))
    if value != 0:
      logger.debug(value)
      abort(value) 

  # ---------------------------------
  # Requests mapping
  # ---------------------------------

  # Misc functions
  app.add_url_rule(settings.API_PREFIX + '/hi', view_func=get_hello, methods=['GET'])

  # Contracts, get signature image
  app.add_url_rule(settings.API_PREFIX + '/signature/<int:id>', view_func=get_signature, methods=['GET'])

  # Airflows plugins - Reports
  app.add_url_rule(settings.API_PREFIX + '/download/<string:name>', view_func=get_download, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/export/<string:name>', view_func=get_export, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/occupancy', view_func=get_occupancy, methods=['GET'])

  # Airflows plugins - Planning
  app.add_url_rule(settings.API_PREFIX + '/availability', view_func=post_availability, methods=['POST'])

  # Airflows plugins - Buttons
  app.add_url_rule(settings.API_PREFIX + '/booking/<int:id>/status/<string:status>', view_func=get_booking_status, methods=['GET'])

  # Airflows plugins - Dashboard
  app.add_url_rule(settings.API_PREFIX + '/dashboard', view_func=get_dashboard, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/dashboard/<string:status>', view_func=get_dashboard, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/labels/<int:id>/<string:locale>', view_func=get_labels, methods=['GET'])

  # Static web (11ty data retrieving)
  app.add_url_rule(settings.API_PREFIX + '/form', view_func=post_form, methods=['POST'])
  app.add_url_rule(settings.API_PREFIX + '/flats/<int:year>', view_func=get_flats, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/rooms/<int:year>', view_func=get_rooms, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/amenities', view_func=get_amenities, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/types', view_func=get_amenities, methods=['GET'])

  # Payment functions
  app.add_url_rule(settings.API_PREFIX + '/pay/<int:id>', view_func=get_pay, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/notify', view_func=post_notification, methods=['POST'])

  # Dynamic web - Booking process - API
  app.add_url_rule(settings.API_PREFIX + '/logout', view_func=post_logout, methods=['POST'])
  app.add_url_rule(settings.API_PREFIX + '/login', view_func=post_login, methods=['POST'])

  # Dynamic web - Booking process - Pages
  app.add_url_rule('/assets/<path:filename>', view_func=get_asset, methods=['GET'])
  app.add_url_rule('/es/booking/<path:filename>', view_func=get_booking, methods=['GET'])
  app.add_url_rule('/booking/<path:filename>', view_func=get_booking, methods=['GET'])

  # Return app
  return app


# #####################################
# Main
# #####################################

if __name__ == '__main__':

  # Run app
  app = runapp()
  app.run(host='0.0.0.0', port=5000, debug=True)
