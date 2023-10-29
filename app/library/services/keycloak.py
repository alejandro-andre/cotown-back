# ###################################################
# Config
# ###################################################

# 1. Crear un nuevo cliente airflows-admin
#  - Access type: confidential
#  - Service account enabled
#  - Root url: https://{{Server}}
# 2. En la pestaña "Service account roles"
#  - En Client roles, seleccionar realm-management
#  - Asignar el rol realm-admin
# 3. En la pestaña "Credentials"
#  - Copiar el client-secret


# ###################################################
# Imports
# ###################################################

# System imports
import requests

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Create user
# ###################################################

def create_keycloak_user(id, firstName, email, username, server, secret):

 # Get access token
 auth_data = {
   'grant_type': 'client_credentials',
   'client_id': 'airflows-admin',
   'client_secret': secret
 }
 response = requests.post('https://' + server + '/auth/realms/airflows/protocol/openid-connect/token', data=auth_data)
 logger.debug('keycloak response->')
 logger.debug(response)
 if response.status_code != 200:
   return False

 # Create user
 api_url = 'https://' + server + '/auth/admin/realms/airflows/users'
 access_token = response.json()['access_token']
 headers = {
   'Authorization': f'Bearer { access_token }',
   'Content-Type': 'application/json'
 }
 user_data = {
   'firstName': str(firstName).strip(),
   'lastName': id, 
   'email': email, 
   'enabled': 'true', 
   'username': username,
   'emailVerified': True,
   'credentials': [
     {
     'type': 'password',
     'value': 'Passw0rd!',
     'temporary': 'true'
     }
   ]
 }
 response = requests.post(api_url, json=user_data, headers=headers)
 logger.debug('keycloak response->')
 logger.debug(response)

 # Error
 if response.status_code > 201:
   return False
 
 # Ok
 return True


# ###################################################
# Delete user
# ###################################################

def delete_keycloak_user(username, server, secret):

 # Get access token
 auth_data = {
   'grant_type': 'client_credentials',
   'client_id': 'airflows-admin',
   'client_secret': secret
 }
 response = requests.post('https://' + server + '/auth/realms/airflows/protocol/openid-connect/token', data=auth_data)
 logger.debug('keycloak token->')
 logger.debug(response)
 if response.status_code != 200:
   return False

 # Get user
 access_token = response.json()['access_token']
 api_url = 'https://' + server + '/auth/admin/realms/airflows/users?lastName=' + username
 headers = {
   'Authorization': f'Bearer { access_token }',
   'Content-Type': 'application/json'
 }
 response = requests.get(api_url, headers=headers)
 logger.debug('keycloak response->')
 logger.debug(response.json())
 if response.json() == []:
   return
  
 # Delete user
 id = response.json()[0]['id']
 logger.debug('keycloak id ', id)
 api_url = 'https://' + server + '/auth/admin/realms/airflows/users/' + id
 headers = {
   'Authorization': f'Bearer { access_token }',
   'Content-Type': 'application/json'
 }
 response = requests.delete(api_url, headers=headers)
 logger.debug('keycloak response->')
 logger.debug(response)
  
 # Ok
 return True