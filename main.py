# #####################################
# Imports
# #####################################

# System includes
import os
from flask import Flask, request, send_file, send_from_directory
from multiprocessing import Process

# Cotown includes
from library.dbclient import DBClient
from library.apiclient import APIClient
from library.keycloak import create_user, delete_user
from library.export import export_to_excel
from library.queries import get_customer, get_provider, availability
from library.redsys import pay, validate
from bill import do_bill
from contract import do_contracts


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

    # DB API
    dbClient = DBClient(SERVER, DATABASE, DBUSER, DBPASS, SSHUSER, SSHPASS)


    # ###################################################
    # Hi
    # ###################################################

    def get_hello():

        print('Hi', flush=True)
        return 'Hi!'


    # ###################################################
    # Static files
    # ###################################################

    def get_html(filename):

        print('HTML ', filename, flush=True)
        return send_from_directory('static', filename + '.html')


    # ###################################################
    # Bill (trigger)
    # ###################################################

    def get_bill(id):

        # Debug
        print('Bill ', id, flush=True)

        # Auth
        token = request.args.get('access_token')
        if token is not None:
            apiClient.auth(token)
        else:
            apiClient.auth(user=GQLUSER, password=GQLPASS)

        # Generate bill
        p = Process(target=do_bill, args=(apiClient, id))
        p.start()
        return 'ok'
    

    # ###################################################
    # Contracts (trigger)
    # ###################################################

    def get_contracts(id):

        # Debug
        print('Contracts ', id, flush=True)

        # Auth
        token = request.args.get('access_token')
        if token is not None:
            apiClient.auth(token)
        else:
            apiClient.auth(user=GQLUSER, password=GQLPASS)

        # Generate contracts
        p = Process(target=do_contracts, args=(apiClient, id))
        p.start()
        return 'ok'
    

    # ###################################################
    # Export to excel
    # ###################################################

    def get_export(name):

        # Debug
        print('Excel ', name, flush=True)

        # Auth
        token = request.args.get('access_token')
        if token is not None:
            apiClient.auth(token)
        else:
            apiClient.auth(user=GQLUSER, password=GQLPASS)
       
        # Querystring variables
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
        print('provider ', data, flush=True)
        if data is not  None:
            print('provider found', flush=True)
    
        # Create keycloak account
        if create_user('P' + str(data['id']), data['Name'], data['Last_name'], data['Email'], 'P' + data['Document']):
            print('provider created', flush=True)

        return
        
    def get_provider_user_add(id):

        print('Provider user add', id, flush=True)
        p = Process(target=provider_user_add, args=(id,))
        p.start()
        return 'ok'


    # ###################################################
    # Create customer user
    # ###################################################

    def customer_user_add(id):

        # Get customer
        data = get_customer(dbClient, id)
        print('customer ', data, flush=True)
        if data is not None:
            print('customer found', flush=True)
    
        # Create keycloak account
        if create_user('C' + str(data['id']), data['Name'], data['Last_name'], data['Email'], 'C' + data['Document']):
            print('customer created', flush=True)
        return

    def get_customer_user_add(id):

        print('Customer user add', id, flush=True)
        p = Process(target=customer_user_add, args=(id,))
        p.start()
        return 'ok'


    # ###################################################
    # Delete provider user
    # ###################################################

    def provider_user_del(id):

        # Delete provider
        if delete_user('P' + str(id)):
            print('provider deleted', flush=True)
        return

    def get_provider_user_del(id):

        print('Provider user del', id, flush=True)
        p = Process(target=provider_user_del, args=(id,))
        p.start()
        return 'ok'


    # ###################################################
    # Delete customer user
    # ###################################################

    def customer_user_del(id):

        # Delete provider
        if delete_user('C' + str(id)):
            print('customer deleted', flush=True)
        return

    def get_customer_user_del(id):

        print('Customer user del', id, flush=True)
        p = Process(target=customer_user_del, args=(id,))
        p.start()
        return 'ok'


    # ###################################################
    # Special queries
    # ###################################################

    # Availability
    def post_availability():

        print('recibido Availability', flush=True)
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

        print('recibido OK', flush=True)
        values = request.values
        print(values.to_dict(), flush=True)
        return 'ok ' + str(values.to_dict())

    # Payment fail
    def get_ko():

        print('recibido KO', flush=True)
        values = request.values
        print(values.to_dict(), flush=True)
        return 'ko ' + str(values.to_dict())

    # Notification
    def post_notification():

        print('recibido Notificacion', flush=True)
        print(request.values, flush=True)
        response = validate(request.values)
        print('[', response, ']', flush=True)
        return 'OK'

    # Payment
    def post_pay():

        # Data
        amount = int(100 * float(request.form.get("amount")))
        order = request.form.get("order")
        return pay(BACK, amount, order)
    

    # ###################################################
    # Flask
    # ###################################################

    # Flask
    app = Flask(__name__)
    
    # Payment
    app.add_url_rule('/notify', view_func=post_notification, methods=['POST'])
    app.add_url_rule('/pay', view_func=post_pay, methods=['POST'])
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
    
    # Run app
    app = runapp()
    app.run(host='0.0.0.0', port=5000, debug=True)
