# ###################################################
# API REST
# ---------------------------------------------------
# Business back office logic for Cotown
# ###################################################

# #####################################
# Imports
# #####################################

# System includes
from flask import Flask, request, abort, make_response, send_file, send_from_directory
from cachetools import TTLCache
from datetime import timedelta
from io import BytesIO
import base64

# Cotown includes
from library.services.dbclient import DBClient
from library.services.apiclient import APIClient
from library.services.cipher import encrypt, decrypt
from library.services.config import settings
from library.services.redsys import pay, validate
from library.services.ac import add_contact
from library.business.export import query_to_excel
from library.business.occupancy import occupancy
from library.business.download import download
from library.business.send_email import smtp_mail
from library.business.queries import *

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
  dbClient = DBClient(settings.SERVER, settings.DATABASE, settings.DBUSER, settings.DBPASS, settings.SSHUSER, settings.SSHPASS)


  # #####################################
  # Cache
  # #####################################

  cache = TTLCache(maxsize=100, ttl=60)


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
  # Get user from cookies
  # ###################################################

  def get_user():

    # Get and decypher cookie
    cookie = request.cookies.get('user')
    if cookie:
      try:
        cookie = json.loads(base64.b64decode(cookie).decode('utf-8'))
        return json.loads(decrypt(base64.b64decode(cookie['credentials']), base64.b64decode(cookie['nonce'])))
      except:
        return None


  # ###################################################
  # Hi
  # ###################################################

  def get_hello():

    logger.debug('Hi')
    return 'Hi!'


  # ###################################################
  # Static files
  # ###################################################

  def get_html(filename):

    # Debug
    logger.debug('HTML ' + filename)

    # Return static file
    try:
      return send_from_directory('static', filename + '.html')
    except:
      return send_from_directory('static', filename)


  # ###################################################
  # Signature
  # ###################################################

  def get_signature(id):

    # Debug
    logger.debug('Signature ' + str(id))

    # Return image
    image = apiClient.getFile(id, 'Provider/Provider_contact', 'Signature')
    response = send_file(BytesIO(image.content), mimetype=image.headers['content-type'])
    return response


  # ###################################################
  # Logout
  # ###################################################

  def post_logout():

    response = make_response(send_file('static/login.html'))
    response.set_cookie('user', '', max_age=0)
    return response


  # ###################################################
  # Login
  # ###################################################

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
  # Form
  # ###################################################

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
      #id = add_contact(contact, listid)
      pass

    # Send email
    logger.info(settings.EMAIL_TO)
    logger.info('Formulario ' + listid) 
    logger.info(json.dumps(contact)) 
    smtp_mail(
      settings.EMAIL_TO, 
      'Formulario ' + listid, 
      json.dumps(contact, indent=2), 
      file=file
    )

    # Return contact ID
    return 'ok'
    return id


  # ###################################################
  # Download files
  # ###################################################

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
  

  # ###################################################
  # Export to excel
  # ###################################################

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
        

  # ###################################################
  # Occupancy report
  # ###################################################

  # Occupancy
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


  # ###################################################
  # Special queries
  # ###################################################

  # Availability
  def post_availability():
    
    data = request.get_json()
    result = availability(
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

  # Web
  def get_prices(year = 2023):

    return prices(dbClient, year)
  
  def get_amenities():

    return amenities(dbClient)

  # Labels
  def get_labels(id, locale):

    return labels(dbClient, id, locale)
  
  # Change booking status
  def get_booking_status(id, status):

    if booking_status(dbClient, id, status):
      return 'ok'
    return 'ko'
  

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
  # Flask
  # ###################################################

  # Flask
  app = Flask(__name__)
  
  # Before each request
  @app.before_request
  def before_request():

    # Debug
    logger.info('Recibido ' + request.path)

    # Get & validate token, if present
    value = validate_token(request.args.get('access_token'))

    # Skip token validaton on public endpoints
    if request.endpoint in ('get_hello', 'post_notification'):
      return

    # Token invalid?
    if value != 0:
      logger.debug(value)
      abort(value) 


  # ---------------------------------
  # Requests without token    
  # ---------------------------------

  # Web login/logout
  app.add_url_rule(settings.API_PREFIX + '/login', view_func=post_login, methods=['POST'])
  app.add_url_rule(settings.API_PREFIX + '/logout', view_func=post_logout, methods=['POST'])

  # Other functions
  app.add_url_rule(settings.API_PREFIX + '/hi', view_func=get_hello, methods=['GET'])

  # Payment functions
  app.add_url_rule(settings.API_PREFIX + '/notify', view_func=post_notification, methods=['POST'])

  # ---------------------------------
  # Requests with  token    
  # ---------------------------------

  # Internal area
  app.add_url_rule(settings.API_PREFIX + '/pay/<int:id>', view_func=get_pay, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/signature/<int:id>', view_func=get_signature, methods=['GET'])

  # Status buttons
  app.add_url_rule(settings.API_PREFIX + '/booking/<int:id>/status/<string:status>', view_func=get_booking_status, methods=['GET'])

  # Planning
  app.add_url_rule(settings.API_PREFIX + '/availability', view_func=post_availability, methods=['POST'])

  # Reports
  app.add_url_rule(settings.API_PREFIX + '/download/<string:name>', view_func=get_download, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/occupancy', view_func=get_occupancy, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/export/<string:name>', view_func=get_export, methods=['GET'])

  # Dashboard
  app.add_url_rule(settings.API_PREFIX + '/dashboard', view_func=get_dashboard, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/dashboard/<string:status>', view_func=get_dashboard, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/labels/<int:id>/<string:locale>', view_func=get_labels, methods=['GET'])

  # Web
  app.add_url_rule(settings.API_PREFIX + '/form', view_func=post_form, methods=['POST'])
  app.add_url_rule(settings.API_PREFIX + '/prices/<int:year>', view_func=get_prices, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/amenities', view_func=get_amenities, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/html/<path:filename>', view_func=get_html, methods=['GET'])

  # Return app
  return app


# #####################################
# Main
# #####################################

if __name__ == '__main__':

  # Run app
  app = runapp()
  app.run(host='0.0.0.0', port=5000, debug=True)
