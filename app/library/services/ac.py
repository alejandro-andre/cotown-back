# #####################################
# Imports
# #####################################

# System includes
import requests

# Cotown includes
from library.services.config import settings

# Logging
import logging
logger = logging.getLogger('COTOWN')


# #####################################
# Constants
# #####################################

AC_URL     = settings.AC_URL
AC_HEADERS = { 'Api-Token': settings.AC_KEY }

FIELDS = [
    { 'field':   '1', 'value': '+44' },           # Edad
    { 'field':   '3', 'value': 'España' },        # Nacionalidad
    { 'field':   '5', 'value': 'Inglés' },        # Idioma
    { 'field':  '27', 'value': 'Experis' },       # Empresa
    { 'field':  '95', 'value': '1000 - 1200' },   # Presupuesto
    { 'field':  '96', 'value': '2023-07-19' },    # F Desde
    { 'field':  '97', 'value': '2023-08-18' },    # F Hasta
    { 'field':  '98', 'value': 'Work' },          # Razón
    { 'field':  '99', 'value': 'LARGE / I_ECO' }, # Tipo de habitación
    { 'field': '100', 'value': 'Balmes 335 ' },   # Edificio
    { 'field': '101', 'value': 'Barcelona' },     # Ciudad
    { 'field': '---', 'value': 'Mensaje...' },    # Mensaje
]


# #####################################
# Prepare contact
# #####################################

def prepare_contact(data):

    contact = {
        'email':       data['email'],
        'firstName':   data['firstName'],
        'lastName':    data['lastName'],
        'phone':       data['phone'],
        'fieldValues': []
    }
    for field in data:
        field = field.split('-')[0]
        if field.isnumeric():
            contact['fieldValues'].append({ 'field': field, 'value': data[field] })
    return { 'contact': contact }


# #####################################
# Get contact
# #####################################

def get_ac_contact(id):

    try:
        url = AC_URL + 'contacts/' + str(id)
        response = requests.get(url, headers=AC_HEADERS)
        return response.json()
    except Exception as error:
        logger.error(error)
        return None

def get_ac_contact_id(email):

    try:
        url = AC_URL + 'contacts?filters[email]=' + email
        response = requests.get(url, headers=AC_HEADERS)
        result = response.json()
        if result and result['contacts']:
            return result['contacts'][0]['id']
    except Exception as error:
        logger.error(error)
        return None


# #####################################
# Create contact
# #####################################

def post_ac_contact(data):

    try:
        url = AC_URL + 'contacts/' + str(id)
        response = requests.post(url, json=prepare_contact(data), headers=AC_HEADERS)
        result = response.json()
        if result and result['contact']:
            return result['contact']['id']

    except Exception as error:
        logger.error(error)
        return None


# #####################################
# Update contact
# #####################################

def put_ac_contact(id, data):

    try:
        url = AC_URL + 'contacts/' + str(id)
        response = requests.put(url, json=prepare_contact(data), headers=AC_HEADERS)
        return response.json()
    except Exception as error:
        logger.error(error)
        return None


# #####################################
# Add contact to list
# #####################################

def post_ac_add_to_list(id, list):

    url = AC_URL + 'contactLists'
    payload = {
       'contactList': {
            'list': str(list),
            'contact': str(id),
            'status': 1
        }
    }
    try:
        response = requests.post(url, json=payload, headers=AC_HEADERS)
        return response.json()
    except Exception as error:
        logger.error(error)
        return None


# #####################################
# Test
# #####################################

def add_contact(data, listid):

    # Check if contact exists
    id = get_ac_contact_id(data['email'])
    logger.info(id)

    # Upsert contact
    if not id:
        logger.info('Creating')
        id = post_ac_contact(data)   
    else:
        logger.info('Updating')
        put_ac_contact(id, data)

    # Add existing contact to list
    if id:
        post_ac_add_to_list(id, listid)
    return id