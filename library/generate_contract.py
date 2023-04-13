# ###################################################
# Imports
# ###################################################

# System includes
from docxtpl import DocxTemplate
from io import BytesIO
import logging
import requests
import jinja2
import datetime

# Logging
import logging
logger = logging.getLogger(__name__)

# Cotown includes
from library.utils import flatten_json


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


# ######################################################
# Additional functions
# ######################################################

def month(m):

  return ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'][m]


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
    logging.error(p, error)
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
  jinja_env = jinja2.Environment()
  jinja_env.filters['month'] = month
  jinja_env.filters['part'] = part

  # Render contract
  doc = DocxTemplate(BytesIO(template))
  doc.render(context, jinja_env)

  # Convert to bytes
  file = BytesIO()
  doc.save(file)
  file.seek(0)
  return file


# ######################################################
# Generate (rent and services) contracts
# ######################################################

def get_template(apiClient, template, rtype, name, ctype):


    # No templates
    if template is None:
      logging.warning(name, 'no tiene plantilla de contrato de', ctype)
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
      logging.warning(name, 'no tiene plantilla de contrato de', ctype, 'para', rtype)
      return None
    
    # Get template
    template = apiClient.getFile(fid, 'Provider/Provider_template', 'Template')
    if template is None:
      logging.warning(name, 'no tiene plantilla de contrato de', ctype)
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
        'name': 'Contrato de renta.docx', 
        'oid': int(oid_rent), 
        'type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' 
      },
      'svcs': { 
        'name': 'Contrato de servicios.docx', 
        'oid': int(oid_svcs), 
        'type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' 
      } 
    }

    # Call graphQL endpoint
    apiClient.call(query, variables)
    return True
  
  except Exception as error:
    logging.error(error)
    return False
