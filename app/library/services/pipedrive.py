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

CRM_URL     = settings.CRM_URL
CRM_HEADERS = { 'x-api-token': settings.CRM_KEY }


# #####################################
# Field mappings
# #####################################

PERSON_FIELDS = [
    {"name": "gender", "key": "351cd467d7da83f3acf733c51255d2aad108aec4", "options": {
        "1": 46,
        "2": 47,
    }},
    {"name": "language", "key": "128cf0d8746a586cd0c57f991f78960fad9e6995", "options": {
        "en": 48,
        "es": 49,
    }},
    {"name": "birth_date",   "key": "f6021c4416b509b585f9b115739aff72baecea0a"},
    {"name": "nationality",  "key": "71bc20441099d4c70f9fa228ed5c212cceee6cfd"},
    {"name": "comments",     "key": "46e73d9e428e2a0bc61571b6774d19bdea7e1179"},
    {"name": "created_date", "key": "3282c86c92e4d61a4a2773cf259f6bed6836a13a"},
]

LEAD_FIELDS = [
    {"name": "type", "key": "12e246ef9250239e04626201d523a70f434d492a", "options": {
        "B2B": 50,
        "B2C": 51,
    }},
    {"name": "channel", "key": "b8bd9aca598fded97ca08b464296d7264cfc53a1", "options": {
        "Marketplace": 52,
        "Directo": 53,
    }},
    {"name": "subchannel", "key": "d8f9aa7278ddcea2701b2f44fa01751974cccbe3", "options": {
        "RRSS": 54,
        "Web": 55,
        "Mail": 56,
        "WhatsApp": 57,
        "Ofi": 58,
        "Teléfono": 59,
        "Referral": 60,
    }},
    {"name": "brand", "key": "7cf0830214bf1caad14cfb6df8e636aaca16895c", "options": {
        "Cotown": 69,
        "Vanguard": 70,
        "VSH": 70,
        "Barcelona residencias - Sardenya": 71,
    }},
    {"name": "web", "key": "03c9da3106ae03ee7d38950e0f8b3afeeb22cdf0", "options": {
        "Cotown": 64,
        "Vanguard": 65,
        "Landing BIO": 66,
        "Landing MAD": 67,
        "Barcelona residencias - Sardenya": 68,
    }},
    {"name": "form", "key": "210ac3f7d81845fdbac509ab585724e8d1ca8c2a", "options": {
        "Formulario Contacto": 72,
        "Chatbot": 73,
        "Formulario Disponibilidad": 115,
        "Formulario Visita": 116,
    }},
    {"name": "reason", "key": "2d1956dbe91e04dbc2e6419ecd74cd242b502bb3", "options": {
        "1": 107,  # Study
        "2": 109,  # Work - Laboral
        "3": 108,  # Study & work
        "4": 110,  # Work - Internship
        "5": 111,  # Holiday - leisure
    }},
    {"name": "building", "key": "b65111dd305fbcb32bd4e27bb9de17eb334d245a", "options": {
        "AMG026": 78, "AVM110": 79, "BAI033": 80, "BLM335": 81, "CCD012": 82,
        "CDC222": 83, "CDC538": 84, "COR207": 85, "CSG396": 86, "DCT075": 87,
        "GCO024": 88, "GTF000": 89, "MUN448": 90, "NAP206": 91, "NAU014": 92,
        "PFC002": 93, "RCF219": 94, "RDC044": 95, "SAL046": 96, "SAR326": 97,
    }},
    {"name": "city", "key": "4d0971ecdd4a2671750b869fe09409ceb95544b3", "options": {
        "Barcelona": 74,
        "Valencia": 75,
        "Madrid": 76,
        "Bilbao": 77,
    }},
    {"name": "place_type",   "key": "7faa69bfe88c3b4b66eeec11b5689e18759f9c53"},
    {"name": "date_from",    "key": "fa49ccea3f47eb227cad47d97f7a1b45369016ef"},
    {"name": "date_to",      "key": "0000cd62bd55a463fe0883b6bd03e75d0d04c412"},
    {"name": "gclid",        "key": "000970d223cd82b73a969c7a8a74f6df965cc0f6"},
    {"name": "utm_content",  "key": "dd28d3ff1301f2af3ca6f28d2fa121472e712e2b"},
    {"name": "utm_term",     "key": "823e2c69755fd840e28efaa28357def1ea6b1de5"},
    {"name": "utm_source",   "key": "bc22feed4254469a0e41c27ec9dc36ca82ab039f"},
    {"name": "utm_medium",   "key": "07101d28f5b3a87e5980d4a466806b7c0b3b41e8"},
    {"name": "utm_campaign", "key": "1a177f5f494e3cdf01890159bd35e4f45592b42d"},
]


def resolve(field_name, value, fields=PERSON_FIELDS):
    name_match = None
    for f in fields:
        if f["name"] != field_name:
            continue
        if name_match is None:
            name_match = f
        opts = f.get("options")
        if opts and value in opts:
            return f["key"], opts[value]
    if name_match is None:
        return None
    if "options" not in name_match:
        return name_match["key"], value
    return name_match["key"], None


# #####################################
# Prepare info
# #####################################

def prepare_person(data):

    result = {
        "name":       (data.get('first_name', '') + ' ' + data.get('last_name', '')).strip(),
        "first_name": data.get('first_name', ''),
        "last_name":  data.get('last_name', ''),
        "phone": [
            { "value": data['phone'], "label": "Personal", "primary": "true" },
        ] if data.get('phone') else [],
        "email": [
            { "value": data['email'], "label": "Personal", "primary": "true" },
        ],
    }
    if data.get('birth_date'):
        result['birthday'] = data['birth_date']
    for field in data:
        resolved = resolve(field.split('-')[0], data[field])
        if resolved:
            key, value = resolved
            if value is not None:
                result[key] = value
    return result


def prepare_lead(data):

    name = (data.get('first_name', '') + ' ' + data.get('last_name', '')).strip() or data.get('email', 'Lead')
    result = {
        "title":     name,
        "person_id": data['person_id'],
        "channel":   3,
    }
    for field in data:
        resolved = resolve(field.split('-')[0], data[field], LEAD_FIELDS)
        if resolved:
            key, value = resolved
            if value is not None:
                result[key] = value
    return result


def prepare_deal(data):

    name = (data.get('first_name', '') + ' ' + data.get('last_name', '')).strip() or data.get('email', 'Deal')
    result = {
        "title":       name,
        "person_id":   data['person_id'],
        "channel":     3,
        "pipeline_id": 3,
        "stage_id":    12,
    }
    for field in data:
        resolved = resolve(field.split('-')[0], data[field], LEAD_FIELDS)
        if resolved:
            key, value = resolved
            if value is not None:
                result[key] = value
    return result


# #####################################
# API calls
# #####################################

def get_person_id_by_email(email):
    response = requests.get(
        f"{CRM_URL}/persons/search",
        headers=CRM_HEADERS,
        params={"term": email, "fields": "email", "limit": 1, "exact_match": "true"},
    )
    response.raise_for_status()
    items = response.json().get("data", {}).get("items", [])
    if not items:
        return None
    return items[0]["item"]["id"]


def upsert_person(data):
    person_id = get_person_id_by_email(data["email"])
    payload = prepare_person(data)
    if person_id:
        response = requests.put(f"{CRM_URL}/persons/{person_id}", headers=CRM_HEADERS, json=payload)
    else:
        response = requests.post(f"{CRM_URL}/persons", headers=CRM_HEADERS, json=payload)
    response.raise_for_status()
    return response.json()["data"]["id"]


def add_lead(data):
    payload = prepare_lead(data)
    response = requests.post(f"{CRM_URL}/leads", headers=CRM_HEADERS, json=payload)
    response.raise_for_status()
    return response.json()["data"]["id"]


def add_deal(data):
    payload = prepare_deal(data)
    response = requests.post(f"{CRM_URL}/deals", headers=CRM_HEADERS, json=payload)
    response.raise_for_status()
    return response.json()["data"]["id"]


# #####################################
# Add info to Pipedrive
# #####################################

def add_info(data):

    # Copy to avoid mutating caller's dict
    data = {**data}

    # Inject fixed values
    data.setdefault('type',       'B2C')
    data.setdefault('channel',    'Directo')
    data.setdefault('subchannel', 'Web')
    data.setdefault('form',       'Formulario Disponibilidad')

    # Normalize field names from forms
    if 'Reason_id' in data:
        data['reason'] = str(data.pop('Reason_id'))
    if 'message' in data:
        data['comments'] = data.pop('message')

    person_id = upsert_person(data)

    data['person_id'] = person_id
    lead_id = add_lead(data)
    deal_id = add_deal(data)

    logger.info(f"Pipedrive: person={person_id} lead={lead_id} deal={deal_id}")
    return person_id