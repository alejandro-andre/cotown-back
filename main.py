# #####################################
# Imports
# #####################################

# System includes
import os
from flask import Flask, request, abort, send_file, send_from_directory

# Cotown includes
from library.dbclient import DBClient
from library.apiclient import APIClient
from library.keycloak import createUser
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
    # Bill
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
        if do_bill(apiClient, id):
            return 'ok'
        abort(500)
    

    # ###################################################
    # Contracts
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
        if do_contracts(apiClient, id):
            return 'ok'
        abort(500)
    

    # ###################################################
    # Create users
    # ###################################################

    @app.route('/provideruser/<int:id>', methods=['GET'])
    def get_provider_user(id):

        # Debug
        print('Provider user ', id)

        # Get token
        token = request.args.get('access_token')
        if token is not None:
            apiClient.auth(token)

        # Get customer
        customer = get_provider(apiClient, id)
        if customer is None:
            abort(404)
    
        # Create keycloak account
        if createUser(customer['Name'], customer['Last_name'], customer['Email'], 'P' + customer['Document']):
            return 'ok'
        abort(500)


    @app.route('/customeruser/<int:id>', methods=['GET'])
    def get_customer_user(id):

        # Debug
        print('Customer user ', id)

        # Get token
        token = request.args.get('access_token')
        if token is not None:
            apiClient.auth(token)

        # Get customer
        customer = get_customer(apiClient, id)
        if customer is None:
            abort(404)
    
        # Create keycloak account
        if createUser(customer['Name'], customer['Last_name'], customer['Email'], 'C' + customer['Document']):
            return 'ok'
        abort(500)


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