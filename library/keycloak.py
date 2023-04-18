# ###################################################
# Config
# ###################################################

# 1. Crear un nuevo cliente airflows-admin
#    - Access type: confidential
#    - Service account enabled
#    - Root url: https://{{server}}
# 2. En la pestaña "Service account roles"
#    - En Client roles, seleccionar realm-management
#    - Asignar el rol realm-admin
# 3. En la pestaña "Credentials"
#    - Copiar el client-secret


# ###################################################
# Imports
# ###################################################

import requests
import os

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Constants
# ###################################################

# Environment variables
SERVER = str(os.environ.get('COTOWN_SERVER'))
SECRET = str(os.environ.get('COTOWN_SECRET'))


# ###################################################
# Create user
# ###################################################

def create_user(id, firstName, email, username):

    # Get access token
    auth_data = {
        'grant_type': 'client_credentials',
        'client_id': 'airflows-admin',
        'client_secret': SECRET
    }
    response = requests.post('https://' + SERVER + '/auth/realms/airflows/protocol/openid-connect/token', data=auth_data)
    logger.debug('keycloak response->')
    logger.debug(response)
    if response.status_code != 200:
        return False

    # Create user
    api_url = 'https://' + SERVER + '/auth/admin/realms/airflows/users'
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

def delete_user(username):

    # Get access token
    auth_data = {
        'grant_type': 'client_credentials',
        'client_id': 'airflows-admin',
        'client_secret': SECRET
    }
    response = requests.post('https://' + SERVER + '/auth/realms/airflows/protocol/openid-connect/token', data=auth_data)
    logger.debug('keycloak token ', response)
    if response.status_code != 200:
        return False

    # Get user
    access_token = response.json()['access_token']
    api_url = 'https://' + SERVER + '/auth/admin/realms/airflows/users?lastName=' + username
    headers = {
        'Authorization': f'Bearer { access_token }',
        'Content-Type': 'application/json'
    }
    response = requests.get(api_url, headers=headers)
    logger.debug('keycloak response ', response.json())
   
    # Delete user
    id = response.json()[0]['id']
    logger.debug('keycloak id ', id)
    api_url = 'https://' + SERVER + '/auth/admin/realms/airflows/users/' + id
    headers = {
        'Authorization': f'Bearer { access_token }',
        'Content-Type': 'application/json'
    }
    response = requests.delete(api_url, headers=headers)
    logger.debug('keycloak response ', response)
   
    # Ok
    return True