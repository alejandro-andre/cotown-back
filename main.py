# #####################################
# Imports
# #####################################

# System includes
import os
from flask import Flask, request, abort, send_file, send_from_directory
from multiprocessing import Process

# Cotown includes
from library.dbclient import DBClient
from library.apiclient import APIClient
from library.keycloak import create_user, delete_user
from library.export import export_to_excel
from library.queries import get_customer, get_provider
from bill import do_bill
from contract import do_contracts


# #####################################
# Flask app
# #####################################

def runapp():

    # ###################################################
    # Environment variables
    # ###################################################

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
    apiClient.auth(user=GQLUSER, password=GQLPASS)

    # DB API
    dbClient = DBClient(SERVER, DATABASE, DBUSER, DBPASS, SSHUSER, SSHPASS)
    dbClient.connect()

    # Flask
    app = Flask(__name__)


    # ###################################################
    # Hi
    # ###################################################

    @app.route('/hello')
    def get_hello():

        print('Hi')
        return 'Hi!'


    # ###################################################
    # Static files
    # ###################################################

    @app.route('/html/<path:filename>')
    def get_html(filename):

        print('HTML ', filename)
        return send_from_directory('static', filename + '.html')


    # ###################################################
    # Bill (trigger)
    # ###################################################

    @app.route('/bill/<int:id>', methods=['GET'])
    def get_bill(id):

        # Debug
        print('Bill ', id)

        # Get token
        token = request.args.get('access_token')
        if token is not None:
            apiClient.auth(token)

        # Generate bill
        p = Process(target=do_bill, args=(apiClient, id))
        p.start()
        return 'ok'
    

    # ###################################################
    # Contracts (trigger)
    # ###################################################

    @app.route('/contracts/<int:id>', methods=['GET'])
    def get_contracts(id):

        # Debug
        print('Contracts ', id)

        # Get token
        token = request.args.get('access_token')
        if token is not None:
            apiClient.auth(token)

        # Generate contracts
        p = Process(target=do_contracts, args=(apiClient, id))
        p.start()
        return 'ok'
    

    # ###################################################
    # Create provider user
    # ###################################################

    def provider_user_add(id):
        
        # Get customer
        data = get_provider(dbClient, id)
        print('provider ', data)
        if data is not  None:
            print('provider found')
    
        # Create keycloak account
        if create_user('P' + str(data['id']), data['Name'], data['Last_name'], data['Email'], 'P' + data['Document']):
            print('provider created')
        return
        
    @app.route('/provideruser/add/<int:id>', methods=['GET'])
    def get_provider_user_add(id):

        print('Provider user add', id)
        p = Process(target=provider_user_add, args=(id,))
        p.start()
        return 'ok'


    # ###################################################
    # Create customer user
    # ###################################################

    def customer_user_add(id):

        # Get customer
        data = get_customer(dbClient, id)
        print('customer ', data)
        if data is not None:
            print('customer found')
    
        # Create keycloak account
        if create_user('C' + str(data['id']), data['Name'], data['Last_name'], data['Email'], 'C' + data['Document']):
            print('customer created')
        return

    @app.route('/customeruser/add/<int:id>', methods=['GET'])
    def get_customer_user_add(id):

        print('Customer user add', id)
        p = Process(target=customer_user_add, args=(id,))
        p.start()
        return 'ok'


    # ###################################################
    # Delete provider user
    # ###################################################

    def provider_user_del(id):

        # Delete provider
        if delete_user('P' + str(id)):
            print('provider deleted')
        return

    @app.route('/provideruser/del/<int:id>', methods=['GET'])
    def get_provider_user_del(id):

        print('Provider user del', id)
        p = Process(target=provider_user_del, args=(id,))
        p.start()
        return 'ok'


    # ###################################################
    # Delete customer user
    # ###################################################

    def customer_user_del(id):

        # Delete provider
        if delete_user('C' + str(id)):
            print('customer deleted')
        return

    @app.route('/customeruser/del/<int:id>', methods=['GET'])
    def get_customer_user_del(id):

        print('Customer user del', id)
        p = Process(target=customer_user_del, args=(id,))
        p.start()
        return 'ok'


    # ###################################################
    # Export to excel
    # ###################################################

    @app.route('/export/<string:name>', methods=['GET'])
    def get_export(name):

        # Debug
        print('Excel ', name)

        # Get token
        token = request.args.get('access_token')
        if token is not None:
            apiClient.auth(token)
       
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


    # Return app
    return app


# #####################################
# Main
# #####################################

if __name__ == '__main__':
    
    # Run app
    app = runapp()
    app.run(host='0.0.0.0', port=5000, debug=True)
