# #####################################
# Imports
# #####################################

# System includes
import os
from flask import Flask, request, send_file, send_from_directory

# Cotown includes
from library.dbclient import DBClient
from library.apiclient import APIClient
from library.export import export_to_excel
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

    # Test
    SERVER   = 'experis.flows.ninja'
    DATABASE = 'niledb'
    DBUSER   = 'postgres'
    DBPASS   = 'postgres'
    GQLUSER  = 'modelsadmin'
    GQLPASS  = 'Ciber$2022'
    SSHUSER  = 'themes'
    SSHPASS  = 'Admin1234!'

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
    def getHello():

        return 'Hi!'


    # ###################################################
    # Static files
    # ###################################################

    @app.route('/html/<path:filename>')
    def getHtml(filename):

        return send_from_directory('static', filename + '.html')


    # ###################################################
    # Bill
    # ###################################################

    @app.route('/bill/<int:id>', methods=['GET'])
    def getBill(id):

        return do_bill(apiClient, id)
    

    # ###################################################
    # Contracts
    # ###################################################

    @app.route('/contracts/<int:id>', methods=['GET'])
    def getContracts(id):

        return do_contracts(apiClient, id)
    

    # ###################################################
    # Export to excel
    # ###################################################

    @app.route('/export/<string:name>', methods=['GET'])
    def getExport(name):

        # Get token
        token = request.args.get('access_token')
        if token == None:
            apiClient.auth(token=None, user=GQLUSER, password=GQLPASS)
        else:
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