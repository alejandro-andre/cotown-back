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
from library.utils import flatten_json


# ######################################################
# Base template for HTML
# ######################################################

BASE = '''
<html>
<head>
<style>
@page {{ size: A4; margin: 1.4cm; }}
body {{ font-size: 12px; font-weight: 400; font-family: Arial, Helvetica, sans-serif; 
}}
table {{ width: 100%; }}
p {{ margin-top: 6px; margin-bottom: 6px; text-align: justify; text-justify: inter-word; }}
ol, ul {{ padding-left: 10px; margin-top: 0; }}
</style>
</head>
<body>{}</body>
</html>
'''


# ######################################################
# Query to retrieve the booking
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
        Owner_template: Provider_templateListViaProvider_id ( where: { Active: { EQ: true }} ) { id Type }
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
        Service_template: Provider_templateListViaProvider_id ( where: { Active: { EQ: true }} ) { id Type }
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
      Customer_email: Email
      Customer_birth_date: Birth_date
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
  text = template.decode('utf-8').replace('\r\n\r\n', '\r\n\r\n<br>\r\n')
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

def get_template(apiClient, template, rtype, name, ctype):


    # No templates
    if template is None:
      logger.warning(name + ' no tiene plantilla de contrato de ' + ctype)
      return None
    
    # Look for proper template
    fid = None
    for c in template:
      if rtype == 'piso' and c['Type'] == 'piso':
        fid = c['id']
        break
      if rtype != 'piso' and c['Type'] != 'piso':
        fid = c['id']
        break
    if fid is None:
      logger.warning(name + ' no tiene plantilla de contrato de ' + ctype + ' para ' + rtype)
      return None
    
    # Get template
    template = apiClient.getFile(fid, 'Provider/Provider_template', 'Template')
    if template is None:
      logger.warning(name + ' no tiene plantilla de contrato de ' + ctype)
    return template
    

def do_contracts(apiClient, id):

  try:
    
    # Get booking info
    variables = { 'id': id }
    result = apiClient.call(BOOKING, variables)
    context = flatten_json(result['data'][0])

    # Get rent template
    template = get_template(apiClient, context.get('Owner_template'), context['Resource_type'], context['Owner_name'], 'renta')
    if template is None:
      return False

    # Generate rent contract
    file = generate_doc_file(context, template.content)
    response = requests.post(
      'https://' + apiClient.server + '/document/Booking/Booking/' + str(id) + '/Contract_rent/contents?access_token=' + apiClient.token, 
      files={'file': file}
    )
    oid_rent = response.content

    # Get services template
    template = get_template(apiClient, context.get('Service_template'), context['Resource_type'], context['Service_name'], 'servicios')
    if template is None:
      return False

    # Generate services contract
    file = generate_doc_file(context, template.content)
    response = requests.post(
      'https://' + apiClient.server + '/document/Booking/Booking/' + str(id) + '/Contract_services/contents?access_token=' + apiClient.token, 
      files={'file': file}
    )
    oid_svcs = response.content

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

    # Update variables
    variables = {
      'id': id, 
      'rent': { 
        'name': 'Contrato de renta.pdf', 
        'oid': int(oid_rent), 
        'type': 'application/pdf' 
      },
      'svcs': { 
        'name': 'Contrato de servicios.pdf', 
        'oid': int(oid_svcs), 
        'type': 'application/pdf' 
      } 
    }

    # Call graphQL endpoint
    apiClient.call(query, variables)
    return True
  
  except Exception as error:
    logger.error(error)
    return False
