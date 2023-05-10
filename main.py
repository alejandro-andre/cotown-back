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

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Cotown includes
from library.services.dbclient import DBClient
from library.services.apiclient import APIClient

from library.services.keycloak import create_keycloak_user, delete_keycloak_user
from library.services.redsys import pay, validate
from library.business.export import export_to_excel
from library.business.send_email import smtp_mail
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
  # Environment variables
  # ###################################################

  BACK   = str(os.environ.get('COTOWN_BACK'))
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
  token = ''

  # DB API
  dbClient = DBClient(SERVER, DATABASE, DBUSER, DBPASS, SSHUSER, SSHPASS)


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

    # Response
    response = send_file(result, mimetype='application/vnd.ms-excel')
    response.headers['Content-Disposition'] = 'inline; filename="' + name + '.xlsx"'
    return response    


  # ###################################################
  # Create provider user
  # ###################################################

  def get_provider_user_add(id):
    
    # Get provider
    data = get_provider(dbClient, id)
    logger.debug('Provider->')
    logger.debug(data)
    if data is not None:
      logger.debug('Provider found')
    else:
      return 'ko'
  
    # Create airflows account
    data['User_name'] = 'p' + data['Document']
    if create_airflows_user(dbClient, data, 200):
      logger.debug('Provider created in Airflows')
    else:
      return 'ko'

    # Create keycloak account
    if create_keycloak_user('p' + str(data['id']), data['Name'], data['Email'], data['User_name']):
      logger.debug('Provider created in Keycloak')
    else:
      return 'ko'

    # Ok
    return 'ok'


  # ###################################################
  # Create customer user
  # ###################################################

  def get_customer_user_add(id):

    # Get customer
    data = get_customer(dbClient, id)
    logger.debug('Customer->')
    logger.debug(data)
    if data is not None:
      logger.debug('Customer found')
    else:
      return 'ko'
  
    # Create airflows account
    data['User_name'] = 'c' + str(id).zfill(6)
    if create_airflows_user(dbClient, data, 300):
      logger.debug('Customer created in Airflows')
    else:
      return 'ko'

    # Create keycloak account
    if create_keycloak_user('c' + str(data['id']), data['Name'], data['Email'], data['User_name']):
      logger.debug('Customer created in Keycloak')
    else:
      return 'ko'

    # Send email
    subject = 'Bienvenido'
    body = 'Accede a https://' + SERVER
    smtp_mail(data['Email'], subject, body)

    # Ok
    return 'ok'


  # ###################################################
  # Delete provider user
  # ###################################################

  def get_provider_user_del(id):

    if delete_keycloak_user('p' + str(id)):
      logger.debug('Provider deleted in keycloak')
      return 'ok'
    return 'ko'
    

  # ###################################################
  # Delete customer user
  # ###################################################

  def get_customer_user_del(id):

    if delete_airflows_user(dbClient, id):
      logger.debug('Customer deleted in airflows')
      return 'ok'
    return 'ko'
         

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
      order   = payment['Payment_order'], 
      amount  = int(100 * float(payment['Amount'])), 
      id    = payment['id'],
      urlok   = 'https://' + SERVER + '/admin/Billing.PaymentOK/external?id=' + payment['Payment_order'],
      urlko   = 'https://' + SERVER + '/admin/Billing.PaymentKO/external?id=' + payment['Payment_order'],
      urlnotify = 'https://' + BACK   + '/notify'
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

    # Get token if present
    token = request.args.get('token')  
    if token is not None:
      apiClient.auth(token)
    else:
      apiClient.auth(user=GQLUSER, password=GQLPASS)
    
  # Payment functions
  app.add_url_rule('/notify', view_func=post_notification, methods=['POST'])
  app.add_url_rule('/pay/<int:id>', view_func=get_pay, methods=['GET'])

  # User management functions
  app.add_url_rule('/provideruser/add/<int:id>', view_func=get_provider_user_add, methods=['GET'])
  app.add_url_rule('/provideruser/del/<int:id>', view_func=get_provider_user_del, methods=['GET'])
  app.add_url_rule('/customeruser/add/<int:id>', view_func=get_customer_user_add, methods=['GET'])
  app.add_url_rule('/customeruser/del/<int:id>', view_func=get_customer_user_del, methods=['GET'])

  # Special queries
  app.add_url_rule('/availability', view_func=post_availability, methods=['POST'])
  app.add_url_rule('/dashboard', view_func=get_dashboard, methods=['GET'])
  app.add_url_rule('/dashboard/<string:status>', view_func=get_dashboard, methods=['GET'])
  app.add_url_rule('/booking/<int:id>/status/<string:status>', view_func=get_booking_status, methods=['GET'])
  app.add_url_rule('/labels/<int:id>/<string:locale>', view_func=get_labels, methods=['GET'])

  # Other functions
  app.add_url_rule('/hi', view_func=get_hello, methods=['GET'])
  app.add_url_rule('/html/<path:filename>', view_func=get_html, methods=['GET'])
  app.add_url_rule('/export/<string:name>', view_func=get_export, methods=['GET'])

  # Return app
  return app


# #####################################
# Main
# #####################################

if __name__ == '__main__':

  # Run app
  app = runapp()
  app.run(host='0.0.0.0', port=5000, debug=True)
