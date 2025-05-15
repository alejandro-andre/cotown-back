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
from flasgger import Swagger, swag_from
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Cotown includes - services
from library.services.dbclient import DBClient
from library.services.apiclient import APIClient
from library.services.config import settings

# Cotown includes - api functions
from library.api.token import validate_token
from library.api.misc import req_pub_hello, req_validate_iban, req_validate_swift, req_cert_booking
from library.api.contract import req_pub_contract
from library.api.booking import req_form, req_typologies, req_pub_asset, req_pub_availability, req_pub_booking
from library.api.airflows import req_signature, req_export, req_href, req_download, req_booking_status, req_labels, req_dashboard_operaciones, req_dashboard_lau, req_dashboard_payments, req_dashboard_deposits, req_dashboard_to_excel, req_prev_next_operaciones, req_availability, req_questionnaire
from library.api.web import req_flats, req_rooms, req_amenities
from library.api.payment import req_pay, req_pub_notification
from library.api.integration import req_pub_int_customers, req_pub_int_invoices, req_pub_int_management_fees

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
    port=settings.get('DBPORT', 5432),
    dbname=settings.DATABASE,
    user=settings.DBUSER,
    password=settings.DBPASS,
    sshuser=settings.SSHUSER,
    sshpassword=settings.get('SSHPASS', None),
    sshprivatekey=settings.get('SSHPKEY', None)
  )
  dbClient.connect()

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
  # Swagger config
  # -------------------------------------------------

  swagger_config = {
      "headers": [],
      "specs": [
          {
              "endpoint": 'cotown_api_spec',
              "route": '/api/cotown_api_spec.json',
              "rule_filter": lambda rule: True,
              "model_filter": lambda tag: True,
          }
      ],
      "static_url_path": "/api/flasgger_static",
      "swagger_ui": True,
      "specs_route": "/api/apidocs/"
  }

  swagger_template = {
      "swagger": "2.0",
      "info": {
          "title": "COTOWN Core 2.0 API",
          "description": "API para acceder a los servicios de Core 2.0 de COTOWN",
          "contact": {
              "responsibleOrganization": "COTOWN SHARING LIFE, S.L.",
              "responsibleDeveloper": "Experis - Manpower Group",
              "email": "hola@cotown.com",
              "url": "https://cotown.com",
          },
          "version": "0.0.1"
      },
      "basePath": "/api/v1",
      "schemes": [ "http", "https" ]
  }
  
  Swagger(app, config=swagger_config, template=swagger_template)

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
    logger.info(f'Recibido {request.path} ({request.endpoint})')
    if not request.endpoint:
      return

    # Global variables
    g.dbClient = dbClient
    g.apiClient = apiClient
    g.env = env

    # Skip token validaton on public endpoints
    if 'flasgger.' in request.endpoint or 'pub_' in request.endpoint:
      return

    # Token invalid?
    value = validate_token(request.args.get('access_token'))
    if value != 0:
      logger.debug(value)
      abort(value)


  # -------------------------------------------------
  # Requests mapping
  # -------------------------------------------------

  # Airflows plugins - Contracts, get signature image
  app.add_url_rule(settings.API_PREFIX + '/signature/<int:id>', view_func=req_signature, methods=['GET'])

  # Airflows plugins - Change location
  app.add_url_rule(settings.API_PREFIX + '/href/<path:path>', view_func=req_href, methods=['GET'])

  # Airflows plugins - Reports
  app.add_url_rule(settings.API_PREFIX + '/download/<string:name>', view_func=req_download, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/export/<string:name>', view_func=req_export, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/report/<string:status>', view_func=req_dashboard_to_excel, methods=['GET'])

  # Airflows plugins - Dashboards
  app.add_url_rule(settings.API_PREFIX + '/dashboard', view_func=req_dashboard_operaciones, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/dashboard/<string:status>', view_func=req_dashboard_operaciones, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/dashboard/prevnext', view_func=req_prev_next_operaciones, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/dashboard/payments', view_func=req_dashboard_payments, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/dashboard/deposits', view_func=req_dashboard_deposits, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/dashboardlau/<string:type>', view_func=req_dashboard_lau, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/labels/<int:id>/<string:locale>', view_func=req_labels, methods=['GET'])

  # Airflows plugins - Planning
  app.add_url_rule(settings.API_PREFIX + '/availability', view_func=req_availability, methods=['POST'])

  # Airflows plugins - Change booking status
  app.add_url_rule(settings.API_PREFIX + '/booking/<int:id>/status/<string:status>', view_func=req_booking_status, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/booking/<int:id>/status/<string:status>/<string:oldstatus>', view_func=req_booking_status, methods=['GET'])

  # Payment functions
  app.add_url_rule(settings.API_PREFIX + '/pay/<int:id>', view_func=req_pay, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/notify', view_func=req_pub_notification, methods=['POST'])
  app.add_url_rule(settings.API_PREFIX + '/notify/<string:pos>', view_func=req_pub_notification, methods=['POST'])
  app.add_url_rule(settings.API_PREFIX + '/iban/<string:code>', view_func=req_validate_iban, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/swift/<string:code>', view_func=req_validate_swift, methods=['GET'])

  # SAP integration
  app.add_url_rule(settings.API_PREFIX + '/integration/customers', view_func=req_pub_int_customers, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/integration/invoices', view_func=req_pub_int_invoices, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/integration/managementfees', view_func=req_pub_int_management_fees, methods=['GET'])

  # Static web (11ty data retrieving)
  app.add_url_rule(settings.API_PREFIX + '/flats/<int:segment>/<int:year>', view_func=req_flats, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/rooms/<int:segment>/<int:year>', view_func=req_rooms, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/amenities/<int:segment>', view_func=req_amenities, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/typologies/<int:segment>', view_func=req_typologies, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/form', view_func=req_form, methods=['POST'])

  # Static web (dynamic availability)
  app.add_url_rule(settings.API_PREFIX + '/availability/<int:type>/<int:filter>', view_func=req_pub_availability, methods=['GET'])
  
  # Dynamic web - Booking process - Pages
  app.add_url_rule('/assets/<path:filename>', view_func=req_pub_asset, methods=['GET'])
  app.add_url_rule('/booking/<int:step>', view_func=req_pub_booking, methods=['GET', 'POST'])

  # Misc functions
  app.add_url_rule(settings.API_PREFIX + '/hi', view_func=req_pub_hello, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/contract', view_func=req_pub_contract, methods=['POST'])
  app.add_url_rule(settings.API_PREFIX + '/cert/<int:booking>', view_func=req_cert_booking, methods=['GET'])
  app.add_url_rule(settings.API_PREFIX + '/questionnaire/<int:id>', view_func=req_questionnaire, methods=['POST'])

  # Return app
  return app


# ###################################################
# Main
# ###################################################

if __name__ == '__main__':

  # Run app
  app = runapp()
  app.run(host='0.0.0.0', port=5000, debug=True)