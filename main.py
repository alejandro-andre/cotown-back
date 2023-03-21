# #####################################
# Imports
# #####################################

# System includes
import json
import os
import io
from flask import Flask, request, send_file, send_from_directory

# Cotown includes
#from library.dbclient import DBClient
from library.apiclient import APIClient
from library.export import export_to_excel
from library.word import contract


# #####################################
# Flask app
# #####################################

def runapp():

    # Environment variables
    os.environ['SERVER'] = 'experis.flows.ninja'
    os.environ['USER'] = 'modelsadmin'
    os.environ['PASS'] = 'Ciber$2022'
    SERVER = str(os.environ.get('SERVER'))
    USER = str(os.environ.get('USER'))
    PASS = str(os.environ.get('PASS'))

    # GraphQL client
    apiClient = APIClient(SERVER)

    # DB client
    #dbClient = DBClient(SERVER, 'niledb', USER, PASS)
    #dbClient.connect()

    # Flask
    app = Flask(__name__)


    # ###################################################
    # Static files
    # ###################################################

    @app.route('/html/<path:filename>')
    def getHtml(filename):

        return send_from_directory('static', filename + '.html')


    # ###################################################
    # Contract
    # ###################################################

    @app.route('/contract/<int:id>', methods=['GET'])
    def getContract(id):

        # Get token
        token = request.args.get('access_token')
        if token == None:
            apiClient.auth(user=USER, password=PASS)
        else:
            apiClient.auth(token=token)

        # Generate contract        
        return contract(apiClient, id)


    # ###################################################
    # Export to excel
    # ###################################################

    @app.route('/export/<string:name>', methods=['GET'])
    def getExport(name):

        # Get token
        token = request.args.get('access_token')
        print(token)
        if token == None:
            apiClient.auth(token=None, user=USER, password=PASS)
        else:
            apiClient.auth(token)
        
        # Query
        fi = open('templates/' + name + '.graphql', 'r')
        query = fi.read()
        fi.close()

        # Columns
        fi = open('templates/' + name + '.json', 'r')
        columns = json.load(fi)
        fi.close()

        # Get template
        fi = open('templates/' + name + '.xlsx', 'rb')
        template = io.BytesIO(fi.read())
       
        # Querystring variables
        vars = {}
        for item in dict(request.args).keys():
            try:
                vars[item] = int(request.args[item])
            except:
                vars[item] = request.args[item]
    
        # Export
        result = export_to_excel(apiClient, query, columns, template, vars)

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