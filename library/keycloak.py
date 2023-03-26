# ###################################################
# Config
# ###################################################

# 1. Crear un nuevo cliente airflows-admin
#    - Access type: confidential
#    - Service account enabled
#    - Root url: https://experis.flows.ninja
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

# ###################################################
# Constants
# ###################################################

# Environment variables
SERVER = str(os.environ.get('COTOWN_SERVER'))
SECRET = str(os.environ.get('COTOWN_SECRET'))


# ###################################################
# Create user
# ###################################################

def createUser(firstName, lastName, email, username):

    # Get access token
    auth_data = {
        'grant_type': 'client_credentials',
        'client_id': 'airflows-admin',
        'client_secret': SECRET
    }
    response = requests.post('https://' + SERVER + '/auth/realms/airflows/protocol/openid-connect/token', data=auth_data)
    if response.status_code != 200:
        return 'ko ' + str(response.status_code)

    # Create user
    api_url = 'https://' + SERVER + '/auth/admin/realms/airflows/users'
    access_token = response.json()['access_token']
    headers = {
        'Authorization': f'Bearer { access_token }',
        'Content-Type': 'application/json'
    }
    user_data = {
        'firstName': firstName,
        'lastName': lastName, 
        'email': email, 
        'enabled': 'true', 
        'username': username,
        'emailVerified': 'true',
        'credentials': [
            {
            'type': 'password',
            'value': 'Passw0rd!',
            'temporary': 'true'
            }
        ]
    }
    response = requests.post(api_url, json=user_data, headers=headers)
    if response.status_code > 201:
        return 'ko ' + str(response.status_code)
    return 'ok'
