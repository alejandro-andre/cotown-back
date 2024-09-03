# #####################################
# Imports
# #####################################

# System includes
import requests


# #####################################
# Constants
# #####################################

AC_URL     = 'https://vanguard-student-housing.api-us1.com/api/3/'
AC_HEADERS = { 'Api-Token': 'b7c07c266ebc3fa5b5b55f9d17c702387b7130b2edd8194e3e9d3900c62cbbe9b3b27859' }

FIELDS = [
    { 'field':   '1', 'value': '+44' },         # Edad
    { 'field':   '3', 'value': 'España' },      # Nacionalidad
    { 'field':   '5', 'value': 'Inglés' },      # Idioma
    { 'field':  '95', 'value': '1000 - 1200' }, # Presupuesto
    { 'field':  '96', 'value': '2023-07-19' },  # F Desde
    { 'field':  '97', 'value': '2023-08-18' },  # F Hasta
    { 'field':  '98', 'value': 'Work' },        # Razón
    { 'field':  '99', 'value': ' Individual room  Standard single' }, # Tipo de habitación
    { 'field': '100', 'value': 'Balmes 335 ' }, # Edificio
    { 'field': '101', 'value': 'Barcelona' },   # Ciudad
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
    except:
        return None

def get_ac_contact_id(email):

    try:
        url = AC_URL + 'contacts?filters[email]=' + email
        response = requests.get(url, headers=AC_HEADERS)
        result = response.json()
        if result and result['contacts']:
            return result['contacts'][0]['id']
    except:
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

    except:
        return None


# #####################################
# Update contact
# #####################################

def put_ac_contact(id, data):

    try:
        url = AC_URL + 'contacts/' + str(id)
        response = requests.put(url, json=prepare_contact(data), headers=AC_HEADERS)
        return response.json()
    except:
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
    except:
        return None


# #####################################
# Test
# #####################################

def main(data, listid):

    # Check if contact exists
    id = get_ac_contact_id(data['email'])
    print(id)

    # Upsert contact
    if not id:
        print('Creating')
        id = post_ac_contact(data)  
    else:
        print('Updating')
        result = put_ac_contact(id, data)

    # Add existing contact to list
    if id:
        post_ac_add_to_list(id, listid)


# #####################################
# Test
# #####################################

if __name__ == '__main__':

    main({
        'email':     'alejandroandre@hotmail.com',
        'firstName': 'Alejandro',
        'lastName':  'André',
        'phone':     '+34 629 25 26 13',

        '1':         '+44',           # Edad
        '3':         'España',        # Nacionalidad
        '37':        'Ciber',         # Empresa
        '95':        '400 - 800',     # Presupuesto
        '96':        '2023-08-01',    # Desde
        '97':        '2024-01-31',    # Hasta
        '98':        'Work',          # Motivo
        '99':        'LARGE / D_SUP', # Tipo de plaza
        '100':       'ART030',        # Edificio
        '101':       'Barcelona',     # Ciudad
    }, 25)