# ###################################################
# API REST
# ---------------------------------------------------
# Business back office logic for Cotown
# ###################################################

# ###################################################
# Imports
# ###################################################

# System includes
from flask import Flask, request, g, abort
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Cotown includes - services
from library.services.dbclient import DBClient
from library.services.apiclient import APIClient
from library.services.config import settings

# Cotown includes - api functions
from library.api.token import validate_token
from library.api.misc import req_hello
from library.api.booking import req_form, req_login, req_logout, req_asset, req_typologies, req_booking
from library.api.airflows import req_signature, req_export, req_occupancy, req_download, req_booking_status, req_labels, req_dashboard, req_availability
from library.api.web import req_flats, req_rooms, req_amenities
from library.api.payment import req_pay, req_notification

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Flask app
# ###################################################

def runapp():

  # -------------------------------------------------
  # Logging
  # -------------------------------------------------

  logger.setLevel(settings.LOGLEVEL)
  console_handler = logging.StreamHandler()
  console_handler.setLevel(settings.LOGLEVEL)
  formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(module)s] [%(funcName)s/%(lineno)d] [%(levelname)s] %(message)s')
  console_handler.setFormatter(formatter)
  logger.addHandler(console_handler)
  logger.info('Started')

  # -------------------------------------------------
  # GraphQL and DB client
  # -------------------------------------------------

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

  # -------------------------------------------------
  # Templating
  # -------------------------------------------------

  env = Environment(
    loader=FileSystemLoader('./booking'),
    autoescape=select_autoescape(['html', 'xml']),
    block_start_string='[%',
    block_end_string='%]',
    variable_start_string='[[',
    variable_end_string=']]'
  )

  # -------------------------------------------------
  # Flask
  # -------------------------------------------------

  # Flask
  app = Flask(__name__)
  app.secret_key = settings.COOKIE_KEY

  # -------------------------------------------------
  # Error handler
  # -------------------------------------------------

  @app.errorhandler(500)
  def internal_error(error):
      return "Lo sentimos, ha ocurrido un error interno.", 500  
  
  # -------------------------------------------------
  # Before each request
  # -------------------------------------------------

  @app.before_request
  def before_request():

    # Debug
    logger.info('Recibido ' + request.path)

    # Global variables
    g.dbClient = dbClient
    g.apiCleint = apiClient
    g.env = env
    
    # Skip token validaton on public endpoints
    if request.endpoint in ('get_hello', 'post_notification', 'get_asset', 'get_booking'):
      return

    # Token invalid?
    value = validate_token(request.args.get('access_token'))
    if value != 0:
      logger.debug(value)
      abort(value) 

  # -------------------------------------------------
  # Requests mapping
  # -------------------------------------------------

  # Misc functions
  app.add_url_rule(settings.API_PREFIX + '/hi', view_func=req_hello, methods=['GET'])

  # Airflows plugins - Contracts, get signature image
  app.add_url_rule(settings.API_PREFIX + '/signature/<int:id>', view_func=req_signature, methods=['GET'])

  # Airflows plugins - Reports
  app.add_url_rule(settings.API_PREFIX + '/download/<string:name>', view_func=req_download, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/export/<string:name>', view_func=req_export, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/occupancy', view_func=req_occupancy, methods=['GET'])

  # Airflows plugins - Planning
  app.add_url_rule(settings.API_PREFIX + '/availability', view_func=req_availability, methods=['POST'])

  # Airflows plugins - Buttons
  app.add_url_rule(settings.API_PREFIX + '/booking/<int:id>/status/<string:status>', view_func=req_booking_status, methods=['GET'])

  # Airflows plugins - Dashboard
  app.add_url_rule(settings.API_PREFIX + '/dashboard', view_func=req_dashboard, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/dashboard/<string:status>', view_func=req_dashboard, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/labels/<int:id>/<string:locale>', view_func=req_labels, methods=['GET'])

  # Static web (11ty data retrieving)
  app.add_url_rule(settings.API_PREFIX + '/flats/<int:segment>/<int:year>', view_func=req_flats, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/rooms/<int:segment>/<int:year>', view_func=req_rooms, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/amenities/<int:segment>', view_func=req_amenities, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/typologies/<int:segment>', view_func=req_typologies, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/form', view_func=req_form, methods=['POST'])

  # Payment functions
  app.add_url_rule(settings.API_PREFIX + '/pay/<int:id>', view_func=req_pay, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/notify', view_func=req_notification, methods=['POST'])

  # Dynamic web - Booking process - Pages
  app.add_url_rule('/logout', view_func=req_logout, methods=['POST'])
  app.add_url_rule('/login', view_func=req_login, methods=['POST'])
  app.add_url_rule('/assets/<path:filename>', view_func=req_asset, methods=['GET'])
  app.add_url_rule('/booking/<int:step>', view_func=req_booking, methods=['GET', 'POST'])

  # Return app
  return app


# ###################################################
# Main
# ###################################################

if __name__ == '__main__':

  # Run app
  app = runapp()
  app.run(host='0.0.0.0', port=5000, debug=True)
