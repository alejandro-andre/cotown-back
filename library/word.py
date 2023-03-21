# ######################################################
# Imports
# ######################################################

from docxtpl import DocxTemplate
from io import BytesIO
import requests
import jinja2
import datetime
import json


# ######################################################
# Additional functions
# ######################################################

def month(m):

  return ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'][m]


# ######################################################
# Flatten JSON
# ######################################################

def flatten_json(json_obj, key='', flattened=None, prefix=''):

  # Empty json, create empty result
  if flattened is None:
    flattened = {}

  # Dictionary, get every key, and flatten each item
  if isinstance(json_obj, dict):
    for key, value in json_obj.items():
      new_prefix = f"{prefix}.{key}" if prefix else key
      flatten_json(value, key, flattened, new_prefix)

  # List, keep the list flattening each element
  elif isinstance(json_obj, list):
    array = []
    for i, value in enumerate(json_obj):
      array.append(flatten_json(value))
    flattened[key] = array

  # Scalar, store item
  else:
    flattened[key] = json_obj

  return flattened


# ######################################################
# Get booking data
# ######################################################

def contract(apiClient, id):

  # Query
  query = '''
  query BookingById ($id: Int!) {
    data: Booking_BookingList (
      where: { id: { EQ: $id } }
    ) {
      Booking_id: id
      Booking_status: Status
      Booking_from_day: Date_from_day
      Booking_from_month: Date_from_month
      Booking_from_year: Date_from_year
      Booking_to_day: Date_to_day
      Booking_to_month: Date_to_month
      Booking_to_year: Date_to_year
      Booking_confirmation_date: Confirmation_date
      Booking_deposit: Deposit
      Booking_second_resident: Second_resident
      ResourceViaResource_id {
        Resource_code: Code
        Resource_type
        Building: BuildingViaBuilding_id {
          Building_code: Code
          Building_address: Address
          DistrictViaDistrict_id {
            LocationViaLocation_id {
              Building_city: Name
            }
          }
        }
        Resource_address: Address
        ProviderViaOwner_id {
          Id_typeViaId_type_id {
            Owner_id_type: Name
          }
          Owner_id: Document
          Owner_name: Name
          Owner_address: Address
          Owner_zip: Zip
          Owner_city: City
          Owner_province: Province
          CountryViaCountry_id {
            Owner_country: Name
          }
          Owner_contacts: Provider_contactListViaProvider_id {
            Name
            Last_name
            Provider_contact_typeViaProvider_contact_type_id {
              Contact_type: Name
            }
          }
        }
        ProviderViaService_id {
          Id_typeViaId_type_id {
            Service_id_type: Name
          }
          Service_id: Document
          Service_name: Name
          Service_address: Address
          Service_zip: Zip
          Service_city: City
          Service_province: Province
          CountryViaCountry_id {
            Service_country: Name
          }
          Service_contacts: Provider_contactListViaProvider_id {
            Name
            Last_name
            Provider_contact_typeViaProvider_contact_type_id {
              Contact_type: Name
            }
          }
        }
      }
      CustomerViaCustomer_id {
        Id_typeViaId_type_id {
          Customer_id_type: Name
        }
        Customer_id: Document
        Customer_name: Name
        Customer_last_name: Last_name
        Customer_address: Address
        Customer_zip: Zip
        Customer_city: City
        Customer_province: Province
        CountryViaCountry_id {
          Customer_country: Name
        }
        Customer_email: Email
        Customer_birth_date: Birth_date
      }
      CustomerViaPayer_id {
        Id_typeViaId_type_id {
          Payer_id_type: Name
        }
        Payer_id: Document
        Payer_name: Name
        Payer_last_name: Last_name
        Payer_address: Address
        Payer_zip: Zip
        Payer_city: City
        Payer_prvince: Province
        CountryViaCountry_id {
          Payer_country: Name
        }
        Payer_email: Email
        Payer_bank_account: Bank_account
      }
      Prices: Booking_priceListViaBooking_id {
        Rent_date
        Rent
        Services
        Rent_discount
        Services_discount
      }
    }
  }
  '''

  # Call graphQL endpoint
  variables = { 'id': id }
  result = apiClient.call(query, variables)

  # Prepare render context
  now = datetime.datetime.now()
  context = flatten_json(result['data'][0])
  context['Today_day'] = now.day
  context['Today_month'] = now.month
  context['Today_year'] = now.year

  # Add custom functions
  jinja_env = jinja2.Environment()
  jinja_env.filters['month'] = month

  # Render contract
  doc = DocxTemplate('templates/contrato.docx')
  doc.render(context, jinja_env)

  # Conver to bytes
  file = BytesIO()
  doc.save(file)
  file.seek(0)

  # Upload file and get OID
  url = 'https://experis.flows.ninja/document/Booking/Booking/' +str(id) + '/Contract_rent/contents?access_token=' + apiClient.token
  response = requests.post(url, files={'file': file})
  oid = response.content

  # Update record
  query = '''
  mutation ($id: Int! $doc: Models_DocumentTypeInputType) {
    Booking_BookingUpdate (
      where:  { id: {EQ: $id} }
      entity: { Contract_rent: $doc }
    ) { id }
  }
  '''

  # Call graphQL endpoint
  variables = {
    'id': id, 
    'doc': { 
      'name': 'Contrato de renta.docx', 
      'oid': int(oid), 
      'type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' 
    } 
  }
  result = apiClient.call(query, variables)
  return ('ok!')