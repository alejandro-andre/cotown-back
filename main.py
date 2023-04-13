# #####################################
# Imports
# #####################################

# System includes
import os
from flask import Flask, request, send_file, send_from_directory
from multiprocessing import Process

# Logging
import logging
logger = logging.getLogger(__name__)

# Cotown includes
from library.dbclient import DBClient
from library.apiclient import APIClient

from library.keycloak import create_user, delete_user
from library.export import export_to_excel
from library.queries import get_customer, get_provider, get_payment, put_payment, availability
from library.redsys import pay, validate
from library.generate_bill import do_bill
from library.generate_contract import do_contracts


# #####################################
# Flask app
# #####################################

def runapp():

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
        return send_from_directory('static', filename + '.html')


    # ###################################################
    # Bill (trigger)
    # ###################################################

    def get_bill(id):

        # Debug
        logger.debug('Bill ' + id)

        # Generate bill in background
        p = Process(target=do_bill, args=(apiClient, id))
        p.start()
        return 'ok'
    

    # ###################################################
    # Contracts (trigger)
    # ###################################################

    def get_contracts(id):

        # Debug
        logger.debug('Contracts ' + id)

        # Generate contracts in background
        p = Process(target=do_contracts, args=(apiClient, id))
        p.start()
        return 'ok'
    

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

    def provider_user_add(id):
        
        # Get customer
        data = get_provider(dbClient, id)
        logger.debug('Provider->')
        logger.debug(data)
        if data is not None:
            logger.debug('Provider found')
    
        # Create keycloak account
        if create_user('P' + str(data['id']), data['Name'], data['Last_name'], data['Email'], 'P' + data['Document']):
            logger.debug('Provider created')

        return
        
    def get_provider_user_add(id):

        logger.debug('Provider user add' + id)
        p = Process(target=provider_user_add, args=(id,))
        p.start()
        return 'ok'


    # ###################################################
    # Create customer user
    # ###################################################

    def customer_user_add(id):

        # Get customer
        data = get_customer(dbClient, id)
        logger.debug('Customer->')
        logger.debug(data)
        if data is not None:
            logger.debug('Customer found')
    
        # Create keycloak account
        if create_user('C' + str(data['id']), data['Name'], data['Last_name'], data['Email'], 'C' + data['Document']):
            logger.debug('Customer created')
        return

    def get_customer_user_add(id):

        logger.debug('Customer user add ' + id)
        p = Process(target=customer_user_add, args=(id,))
        p.start()
        return 'ok'


    # ###################################################
    # Delete provider user
    # ###################################################

    def provider_user_del(id):

        # Delete provider
        if delete_user('P' + str(id)):
            logger.debug('Provider deleted')
        return

    def get_provider_user_del(id):

        logger.debug('Provider user del' + id)
        p = Process(target=provider_user_del, args=(id,))
        p.start()
        return 'ok'


    # ###################################################
    # Delete customer user
    # ###################################################

    def customer_user_del(id):

        # Delete provider
        if delete_user('C' + str(id)):
            logger.debug('Customer deleted')
        return

    def get_customer_user_del(id):

        logger.debug('Customer user del' + id)
        p = Process(target=customer_user_del, args=(id,))
        p.start()
        return 'ok'


    # ###################################################
    # Special queries
    # ###################################################

    # Availability
    def post_availability():

        data = request.get_json()
        return availability(
            dbClient, 
            date_from=data.get('date_from'), 
            date_to=data.get('date_to'), 
            building=data.get('building', ''), 
            place_type=data.get('place_type', '')
        )
    

    # ###################################################
    # Payments
    # ###################################################

    # Payment Ok
    def get_ok():

        values = request.values
        logger.debug(values.to_dict())
        return 'ok ' + str(values.to_dict())

    # Payment fail
    def get_ko():

        values = request.values
        logger.debug(values.to_dict())
        return 'ko ' + str(values.to_dict())

    # Prepare payment params
    def get_pay(id):

        # Get payment
        payment = get_payment(dbClient, id, generate_order=True)
        logger.debug(payment)
    
        # Redsys data
        params = pay(
            order     = payment['Payment_order'], 
            amount    = int(100 * float(payment['Amount'])), 
            id        = payment['id'],
            urlok     = 'https://' + SERVER + '/admin/Billing.PaymentOK/external?id=' + payment['Payment_order'],
            urlko     = 'https://' + SERVER + '/admin/Billing.PaymentKO/external?id=' + payment['Payment_order'],
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
        
    # Payment
    app.add_url_rule('/notify', view_func=post_notification, methods=['POST'])
    app.add_url_rule('/pay/<int:id>', view_func=get_pay, methods=['GET'])
    app.add_url_rule('/ok', view_func=get_ok, methods=['GET'])
    app.add_url_rule('/ko', view_func=get_ko, methods=['GET'])

    # Keycloak functions
    app.add_url_rule('/provideruser/add/<int:id>', view_func=get_provider_user_add, methods=['GET'])
    app.add_url_rule('/provideruser/del/<int:id>', view_func=get_provider_user_del, methods=['GET'])
    app.add_url_rule('/customeruser/add/<int:id>', view_func=get_customer_user_add, methods=['GET'])
    app.add_url_rule('/customeruser/del/<int:id>', view_func=get_customer_user_del, methods=['GET'])

    # Special queries
    app.add_url_rule('/availability', view_func=post_availability, methods=['POST'])

    # Main functions
    app.add_url_rule('/hi', view_func=get_hello, methods=['GET'])
    app.add_url_rule('/html/<path:filename>', view_func=get_html, methods=['GET'])
    app.add_url_rule('/bill/<int:id>', view_func=get_bill, methods=['GET'])
    app.add_url_rule('/contracts/<int:id>', view_func=get_contracts, methods=['GET'])
    app.add_url_rule('/export/<string:name>', view_func=get_export, methods=['GET'])

    # Return app
    return app


# #####################################
# Main
# #####################################

if __name__ == '__main__':

    # Logging    
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Run app
    app = runapp()
    logger.info('Started')
    app.run(host='0.0.0.0', port=5000, debug=True)
