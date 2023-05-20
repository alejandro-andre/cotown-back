# ###################################################
# API REST
# ---------------------------------------------------
# Business back office logic for Cotown
# ###################################################

# #####################################
# Imports
# #####################################

# System includes
import os
from flask import Flask, request, abort, send_file, send_from_directory
from cachetools import TTLCache

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Cotown includes
from library.services.dbclient import DBClient
from library.services.apiclient import APIClient
from library.services.redsys import pay, validate
from library.business.export import export_to_excel
from library.business.queries import *


# #####################################
# Flask app
# #####################################

def runapp():

  # ###################################################
  # Logging
  # ###################################################

  logger.setLevel(logging.DEBUG)
  console_handler = logging.StreamHandler()
  console_handler.setLevel(logging.DEBUG)
  formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(module)s] [%(levelname)s] %(message)s')
  console_handler.setFormatter(formatter)
  logger.addHandler(console_handler)
  logger.info('Started')


  # ###################################################
  # Constants
  # ###################################################

  API_PREFIX = '/api/v1'


  # ###################################################
  # Environment variables
  # ###################################################

  BACK     = str(os.environ.get('COTOWN_BACK'))
  SERVER   = str(os.environ.get('COTOWN_SERVER'))
  DATABASE = str(os.environ.get('COTOWN_DATABASE'))
  DBUSER   = str(os.environ.get('COTOWN_DBUSER'))
  DBPASS   = str(os.environ.get('COTOWN_DBPASS'))
  GQLUSER  = str(os.environ.get('COTOWN_GQLUSER'))
  GQLPASS  = str(os.environ.get('COTOWN_GQLPASS'))
  SSHUSER  = str(os.environ.get('COTOWN_SSHUSER'))
  SSHPASS  = str(os.environ.get('COTOWN_SSHPASS'))


  # ###################################################
  # GraphQL and DB client
  # ###################################################

  # graphQL API
  apiClient = APIClient(SERVER)

  # DB API
  dbClient = DBClient(SERVER, DATABASE, DBUSER, DBPASS, SSHUSER, SSHPASS)


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
        result = apiClient.call('{ user: getCurrentUser { currentUser } }')
        if result['user']['currentUser'] != 'anonymous':
          result = 0
      except:
        pass
      cache[token] = result

    # Debug / Remove in production
    apiClient.auth(user=GQLUSER, password=GQLPASS)
    logger.warning('Acceso sin token')
    result = 0

    # Forbidden
    return result


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

    logger.debug('HTML ' + filename)
    try:
      return send_from_directory('static', filename + '.html')
    except:
      return send_from_directory('static', filename)


  # ###################################################
  # Export to excel
  # ###################################################

  def get_export(name):

    # Debug
    logger.debug('Excel ' + name)

    # Querystring variables, try int by default
    vars = {}
    for item in dict(request.args).keys():
      try:
        vars[item] = int(request.args[item])
      except:
        vars[item] = request.args[item]
  
    # Export
    result = export_to_excel(apiClient, name, vars)
    if result is None:
      return 'ko'

    # Response
    response = send_file(result, mimetype='application/vnd.ms-excel')
    response.headers['Content-Disposition'] = 'inline; filename="' + name + '.xlsx"'
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
      urlok     = 'https://' + BACK + '/customer/pago_ok?id=' + payment['Payment_order'],
      urlko     = 'https://' + BACK + '/customer/pago_ko?id=' + payment['Payment_order'],
      urlnotify = 'https://' + BACK + API_PREFIX + '/notify'
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
      abort(value) 


  # ---------------------------------
  # Requests without token    
  # ---------------------------------

  # Other functions
  app.add_url_rule(API_PREFIX + '/hi', view_func=get_hello, methods=['GET'])

  # Payment functions
  app.add_url_rule(API_PREFIX + '/notify', view_func=post_notification, methods=['POST'])

  # ---------------------------------
  # Requests with  token    
  # ---------------------------------

  # Payment functions
  app.add_url_rule(API_PREFIX + '/pay/<int:id>', view_func=get_pay, methods=['GET'])

  # Planning
  app.add_url_rule(API_PREFIX + '/availability', view_func=post_availability, methods=['POST'])

  # Dashboard
  app.add_url_rule(API_PREFIX + '/dashboard', view_func=get_dashboard, methods=['GET'])
  app.add_url_rule(API_PREFIX + '/dashboard/<string:status>', view_func=get_dashboard, methods=['GET'])
  app.add_url_rule(API_PREFIX + '/labels/<int:id>/<string:locale>', view_func=get_labels, methods=['GET'])

  # Status buttons
  app.add_url_rule(API_PREFIX + '/booking/<int:id>/status/<string:status>', view_func=get_booking_status, methods=['GET'])

  # Export
  app.add_url_rule(API_PREFIX + '/html/<path:filename>', view_func=get_html, methods=['GET'])
  app.add_url_rule(API_PREFIX + '/export/<string:name>', view_func=get_export, methods=['GET'])

    # Return app
  return app


# #####################################
# Main
# #####################################

if __name__ == '__main__':

  # Run app
  app = runapp()
  app.run(host='0.0.0.0', port=5000, debug=True)
