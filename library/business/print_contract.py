# ###################################################
# Imports
# ###################################################

# System includes
import markdown
import logging
import requests
import datetime
from jinja2 import Environment
from weasyprint import HTML
from io import BytesIO

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Cotown includes
from library.services.utils import flatten_json


# ######################################################
# Base template for HTML
# ######################################################

BASE = '''
<html>
<head>
<style>
@page {{ size: A4; margin: 1.4cm; }}
body {{ font-size: 14px; font-weight: 400; font-family:"Calibri", Arial, Helvetica, sans-serif; 
}}
table {{ width: 100%; }}
p {{ margin-top: 18px; margin-bottom: 18px; text-align: justify; text-justify: inter-word; }}
ol, ul {{ padding-left: 10px; margin-top: 0; }}
li {{ list-style-position: outside; }}
h1 {{ font-size: 1em; font-weight: 600; text-align: center; }}
h2 {{ font-size: 1em; font-weight: 600; }}
h3 {{ font-size: 1em; font-weight: 600; }}
</style>
</head>
<body>{}</body>
</html>
'''


# ######################################################
# Querys to retrieve the bookings
# ######################################################

BOOKING = '''
query BookingById ($id: Int!) {
  data: Booking_BookingList (
    where: { id: { EQ: $id } }
  ) {
    Booking_id: id
    Booking_status: Status
    Booking_date_from_day: Date_from_day
    Booking_date_from_month: Date_from_month
    Booking_date_from_year: Date_from_year
    Booking_date_to_day: Date_to_day
    Booking_date_to_month: Date_to_month
    Booking_date_to_year: Date_to_year
    Booking_confirmation_date: Confirmation_date
    Booking_deposit: Deposit
    Booking_rent: Rent
    Booking_services: Services
    Booking_limit: Limit
    Booking_second_resident: Second_resident
    ResourceViaResource_id {
      Resource_code: Code
      Resource_type
      Resource_part: Part
      Resource_address: Address
      Building: BuildingViaBuilding_id {
        Building_code: Code
        Building_address: Address
        DistrictViaDistrict_id {
          LocationViaLocation_id {
            Building_city: Name
          }
        }
      }
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
        Owner_signer_name: Signer_name
        Id_typeViaSigner_Id_type_id {
          Owner_signer_id_type: Name
        }
        Owner_signer_id: Signer_document
        Owner_template: Provider_templateListViaProvider_id ( where: { Active: { EQ: true }} ) { id Name Type }
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
        Service_signer_name: Signer_name
        Id_typeViaSigner_Id_type_id {
          Service_signer_id_type: Name
        }
        Service_signer_id: Signer_document
        Service_template: Provider_templateListViaProvider_id ( where: { Active: { EQ: true }} ) { id Name Type }
      }
    }
    CustomerViaCustomer_id {
      Id_typeViaId_type_id {
        Customer_id_type: Name
      }
      Customer_id: Document
      Customer_name: Name
      Customer_address: Address
      Customer_zip: Zip
      Customer_city: City
      Customer_province: Province
      CountryViaCountry_id {
        Customer_country: Name
      }
      CountryViaNationality_id {
          Customer_nationality: Name
      }
      Customer_email: Email
      Customer_birth_date: Birth_date
      Customer_tutor_id: Tutor_id
    }
    CustomerViaPayer_id {
      Id_typeViaId_type_id {
        Payer_id_type: Name
      }
      Payer_id: Document
      Payer_name: Name
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

GROUP_BOOKING = '''
query Booking_groupById ($id: Int!) {
  data: Booking_Booking_groupList (
    where: { id: { EQ: $id } }
  ) {
    Booking_id: id
    Booking_status: Status
    Booking_date_from_day: Date_from_day
    Booking_date_from_month: Date_from_month
    Booking_date_from_year: Date_from_year
    Booking_date_to_day: Date_to_day
    Booking_date_to_month: Date_to_month
    Booking_date_to_year: Date_to_year
    Booking_rent: Rent
    Booking_services: Services
    Booking_limit: Limit
    Booking_deposit: Deposit
    Booking_limit: Limit
    CustomerViaPayer_id {
      Id_typeViaId_type_id {
        Payer_id_type: Name
      }
      Payer_id: Document
      Payer_name: Name
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
    Room: Booking_roomingListViaBooking_id {
        ResourceViaResource_id {
            Resource_code: Code
            Resource_type
            Resource_part: Part
            Resource_address: Address
            Building: BuildingViaBuilding_id {
                Building_code: Code
                Building_address: Address
                DistrictViaDistrict_id {
                LocationViaLocation_id {
                    Building_city: Name
                }
                }
            }
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
                Owner_signer_name: Signer_name
                Id_typeViaSigner_Id_type_id {
                Owner_signer_id_type: Name
                }
                Owner_signer_id: Signer_document
                Owner_template: Provider_templateListViaProvider_id ( where: { Active: { EQ: true }} ) { id Name Type }
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
                Service_signer_name: Signer_name
                Id_typeViaSigner_Id_type_id {
                Service_signer_id_type: Name
                }
                Service_signer_id: Signer_document
                Service_template: Provider_templateListViaProvider_id ( where: { Active: { EQ: true }} ) { id Name Type }
            }
        }
          Id_typeViaId_type_id {
            Customer_id_type: Name
        }
        Customer_id: Document
        Customer_name: Name
        Customer_address: Address
        Customer_zip: Zip
        Customer_city: City
        Customer_province: Province
        CountryViaCountry_id {
            Customer_country: Name
        }
        Customer_email: Email
    }
    Prices: Booking_group_priceListViaBooking_id {
      Rent_date
      Rent
      Services
    }
  }
}
'''


# ######################################################
# Additional functions
# ######################################################

def month(m):

  try:
    return ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'][m-1]
  except:
    return '--'


def part(p):

  if p is None:
    return ''

  try:  
    s = ''
    part = [
      '', '', 'media', 'tercera', 'cuarta', 'quinta', 'sexta', 'septima', 'octava', 'novena', 'décima', 'onceava', 'doceava', 'treceava', 'catorceava', 'quinceava'
    ][int(p[2:])]
    n, s = ('una ', '') if p[0] == '1' else ('dos ', 's')
    return n + part + s + ' parte' + s +' (' + p + ' parte' + s + ')'
  except Exception as error:
    logger.error(p)
    logger.error(error)
    return p


# ######################################################
# Generate document file
# ######################################################

def generate_doc_file(context, template):

  # Prepare render context
  now = datetime.datetime.now()
  context['Today_day'] = now.day
  context['Today_month'] = now.month
  context['Today_year'] = now.year

  # Add custom functions
  env = Environment()
  env.filters['month'] = month
  env.filters['part'] = part

  # Render contract
  text = template.decode('utf-8').replace('\r\n\r\n\r\n', '\r\n\r\n&nbsp;\r\n\r\n')
  md = env.from_string(text).render(context)

  # Convert markdown to HTML
  doc = BASE.format(markdown.markdown(md, extensions=['tables', 'attr_list']))

  # Return file
  file = BytesIO()
  html = HTML(string=doc)
  html.write_pdf(file)
  file.seek(0)

  # Render docx contract
  #doc = DocxTemplate(BytesIO(template))
  #doc.render(context, env)

  return file


# ######################################################
# Generate (rent and services) contracts
# ######################################################

def get_template(apiClient, tpl, rtype, provider):

    # Fix
    if rtype == 'plaza':
      rtype = 'habitacion'
    
    # No templates
    if tpl is None:
      logger.warning(provider + ' no tiene plantillas de contrato')
      return None, None
    
    # Look for proper template
    fid = None
    fname = ''
    for c in tpl:
      if rtype == c['Type']:
        fid = c['id']
        fname = c['Name']
        break
    if fid is None:
      logger.warning(provider + ' no tiene plantilla de contrato de ' + rtype)
      return None, None

    # Get template
    template = apiClient.getFile(fid, 'Provider/Provider_template', 'Template')
    if template is None:
      logger.warning(provider + ' no se encuentra la plantilla de contrato de ' + rtype)
    return template, fname
    

def do_contracts(apiClient, id):

  try:
    
    # Empty files
    json_rent = None
    json_svcs = None

    # Get booking info
    variables = { 'id': id }
    result = apiClient.call(BOOKING, variables)
    context = flatten_json(result['data'][0])

    # Generate rent contract
    template, name = get_template(apiClient, context['Owner_template'], context['Resource_type'], context['Owner_name'])
    if template is not None:
      file = generate_doc_file(context, template.content)
      response = requests.post(
        'https://' + apiClient.server + '/document/Booking/Booking/' + str(id) + '/Contract_rent/contents?access_token=' + apiClient.token, 
        files={'file': file}
      )
      json_rent = { 'name': name + '.pdf', 'oid': int(response.content), 'type': 'application/pdf' }

    # Generate services contract
    if context['Owner_id'] != context['Service_id']:
      template, name = get_template(apiClient, context['Service_template'], context['Resource_type'], context['Service_name'])
      if template is not None:
        file = generate_doc_file(context, template.content)
        response = requests.post(
          'https://' + apiClient.server + '/document/Booking/Booking/' + str(id) + '/Contract_services/contents?access_token=' + apiClient.token, 
          files={'file': file}
        )
        json_svcs = { 'name': name + '.pdf', 'oid': int(response.content), 'type': 'application/pdf' }

    # Update query
    query = '''
    mutation ($id: Int! $rent: Models_DocumentTypeInputType $svcs: Models_DocumentTypeInputType) {
      Booking_BookingUpdate (
        where:  { id: {EQ: $id} }
        entity: { 
          Contract_rent: $rent 
          Contract_services: $svcs
        }
      ) { id }
    }
    '''

    # Call graphQL endpoint
    if json_rent is not None or json_svcs is not None:
      apiClient.call(query, { 'id': id, 'rent': json_rent, 'svcs': json_svcs })
      return True
    return False
  
  except Exception as error:
    logger.error(error)
    return False


def do_group_contracts(apiClient, id):

  try:
    
    # Empty files
    json_rent = None
    json_svcs = None

    # Get booking info
    variables = { 'id': id }
    result = apiClient.call(GROUP_BOOKING, variables)
    context = flatten_json(result['data'][0])
    room = context['Room'][0]

    # Generate rent contract
    template, name = get_template(apiClient, room['Owner_template'], 'grupo', room['Owner_name'])
    if template is not None:
      file = generate_doc_file(context, template.content)
      response = requests.post(
        'https://' + apiClient.server + '/document/Booking/Booking_group/' + str(id) + '/Contract_rent/contents?access_token=' + apiClient.token, 
        files={'file': file}
      )
      json_rent = { 'name': name + '.pdf', 'oid': int(response.content), 'type': 'application/pdf' }

    # Generate services contract
    if context['Service_id'] is not None and context['Owner_id'] != context['Service_id']:
      template, name = get_template(apiClient, room['Service_template'], 'grupo', room['Service_name'])
      if template is not None:
        file = generate_doc_file(context, template.content)
        response = requests.post(
          'https://' + apiClient.server + '/document/Booking/Booking_group/' + str(id) + '/Contract_services/contents?access_token=' + apiClient.token, 
          files={'file': file}
        )
        json_svcs = { 'name': name + '.pdf', 'oid': int(response.content), 'type': 'application/pdf' }

    # Update query
    query = '''
    mutation ($id: Int! $rent: Models_DocumentTypeInputType $svcs: Models_DocumentTypeInputType) {
      Booking_Booking_groupUpdate (
        where:  { id: {EQ: $id} }
        entity: { 
          Contract_rent: $rent 
          Contract_services: $svcs
        }
      ) { id }
    }
    '''

    # Call graphQL endpoint
    if json_rent != '{}' or json_svcs != '{}':
      apiClient.call(query, { 'id': id, 'rent': json_rent, 'svcs': json_svcs })
      return True
    return False
  
  except Exception as error:
    logger.error(error)
    return False