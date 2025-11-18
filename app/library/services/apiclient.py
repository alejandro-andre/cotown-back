# ###################################################
# Imports
# ###################################################

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import requests

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Class APIClient
# ###################################################

class APIClient:

  # Initializes object
  def __init__(self, server):

    # Attributes
    self.server = server
    self.token = ''
    self.headers = {}

    # Create GraphQL client
    transport = AIOHTTPTransport(url=f'https://{server}/graphql', headers=self.headers)
    self.client = Client(transport=transport, fetch_schema_from_transport=True)


  # Sets token
  def auth(self, token=None, user=None, password=None):

    # Set token
    if token is not None:
      self.token = token
      self.headers["Authorization"] = f"Bearer {self.token}"
      self.client.transport.headers = self.headers
      return
 
    # Get auth token
    try:
      result = self.client.execute(gql('mutation { login(username:"' + user + '", password:"' + password + '") }'))
      self.token = result['login']
      self.headers["Authorization"] = f"Bearer {self.token}"
      self.client.transport.headers = self.headers
    except Exception as e:
      logger.error(e)


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
  def getFile(self, id, entity, field='File'):

    # Get file from Airflows
    url = 'https://' + self.server + '/wopi/files/' + entity + '/' + str(id) + '/' + field + '/contents?inline=true&access_token=' + self.token
    headers = { 'Authorization': f'Bearer {self.token}'}
    result = requests.get(url, headers=headers)
    return result

