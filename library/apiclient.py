# ###################################################
# Imports
# ###################################################

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import requests


# ###################################################
# Class APIClient
# ###################################################

class APIClient:

    # Initializes object
    def __init__(self, server):

        # Attributes
        self.server = server
        self.token = ''

        # Create GraphQL client
        self.client = Client(transport=AIOHTTPTransport(url='https://' + server + '/graphql'), fetch_schema_from_transport=True)


    # Sets token
    def auth(self, token=None, user=None, password=None):

        # Get auth token
        result = self.client.execute(gql('mutation { login(username:"' + user + '", password:"' + password + '") }'))
        self.token = result['login']


    # Call endpoint
    def call(self, query, vars=None):

        # Prepare variables
        if vars is None:
            vars = {'authorization': self.token}
        else:
            vars['authorization'] = self.token

        # Call API
        return self.client.execute(gql(query), vars)
    

    # Get file
    def getFile(self, entity, id):

        # Get file from Airflows
        return requests.get(
            'https://experis.flows.ninja/wopi/files/'
            + entity
            + '/'
            + str(id)
            + '/File/contents?inline=true&access_token=' 
            + self.token
        )

