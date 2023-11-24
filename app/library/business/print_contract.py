# ###################################################
# Imports
# ###################################################

# System includes
import markdown
import requests
import locale
from num2words import num2words
from datetime import datetime
from jinja2 import Environment
from weasyprint import HTML
from io import BytesIO

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Cotown includes
from library.services.config import settings
from library.services.utils import flatten


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
hr {{ border-top: 0px; page-break-after: always; }}
img[alt=firma] {{ width: 200px; }}
</style>
</head>
<body>{}</body>
</html>
'''


# ######################################################
# Querys to retrieve the bookings
# ######################################################

BOOKING = '''
query BookingById ($id: Int) {
  data: Booking_BookingList (
    where: { id: { EQ: $id } }
  ) {     
    Booking_id: id
    Booking_status: Status
    Booking_date_from: Date_from
    Booking_date_to: Date_to
    Booking_date_from_day: Date_from_day
    Booking_date_from_month: Date_from_month
    Booking_date_from_year: Date_from_year
    Booking_date_to_day: Date_to_day
    Booking_date_to_month: Date_to_month
    Booking_date_to_year: Date_to_year
    Booking_confirmation_date: Confirmation_date
    Booking_rent: Rent
    Booking_services: Services
    Booking_deposit: Deposit
    Booking_limit: Limit
    Booking_final_cleaning: Final_cleaning
    Booking_second_resident: Second_resident
    Customer_reasonViaReason_id {
        Booking_reason: Name
    }
    SchoolViaSchool_id {
        Booking_school: Name
    }
    Cancelation_fee
    Cancel_date
    Resource_flat_typeViaFlat_type_id {
      Booking_flat_type_code: Code
      Booking_flat_type_name: Name
    }
    Resource_place_typeViaPlace_type_id {
      Booking_place_type_code: Code
      Booking_place_type_name: Name
    }
    BuildingViaBuilding_id {
      Booking_building_code: Code
      Booking_building_name: Name
      Booking_building_address: Address
      Booking_building_type: Building_type_id
      DistrictViaDistrict_id {
        LocationViaLocation_id {
          Booking_building_city: Name
        }
      }
      Services: Building_serviceListViaBuilding_id {
        Building_service_typeViaService_id (
            joinType: INNER
            where: { Contract: { EQ: true } }
        ) {
            Name
        }
      }
    }
    ResourceViaResource_id {
      Resource_code: Code
      Resource_type
      Resource_part: Part
      Resource_address: Address
      Resource_street: Street
      Flat: ResourceViaFlat_id {
        Resource_flat_code: Code
        Resource_flat_address: Address
        Resource_flat_street: Street
      }
      Building: BuildingViaBuilding_id {
        Resource_building_code: Code
        Resource_building_address: Address
        SegmentViaSegment_id {
            Segment_name: Name
            Segment_url: Url
        }
        DistrictViaDistrict_id {
          LocationViaLocation_id {
            Resource_building_city: Name
          }
        }
      }
      ProviderViaOwner_id {
        Id_typeViaId_type_id {
          Owner_id_type: Name
        }
        Owner_id: Document
        Owner_name: Name
        Owner_email: Email
        Owner_address: Address
        Owner_zip: Zip
        Owner_city: City
        Owner_province: Province
        CountryViaCountry_id {
          Owner_country: Name
        }
        Owner_signers: Provider_contactListViaProvider_id (
          where: { Provider_contact_type_id: { EQ: 1 } }
        ) {
          Owner_signer: id
          Owner_signer_name: Name
          Id_typeViaId_type_id {
            Owner_signer_id_type: Name
          }
          Owner_signer_id: Document
        }
        Owner_template: Provider_templateListViaProvider_id ( where: { Active: { EQ: true }} ) { id Name Type Contract_id }
      }
      ProviderViaService_id {
        Id_typeViaId_type_id {
          Service_id_type: Name
        }
        Service_id: Document
        Service_name: Name
        Service_email: Email
        Service_address: Address
        Service_zip: Zip
        Service_city: City
        Service_province: Province
        CountryViaCountry_id {
          Service_country: Name
        }
        Service_signers: Provider_contactListViaProvider_id (
          where: { Provider_contact_type_id: { EQ: 1 } }
        ) {
          Service_signer: id
          Service_signer_name: Name
          Id_typeViaId_type_id {
            Service_signer_id_type: Name
          }
          Service_signer_id: Document
        }
        Service_template: Provider_templateListViaProvider_id ( where: { Active: { EQ: true }} ) { id Name Type Contract_id }
      }
    }
    CustomerViaCustomer_id {
      Customer_type: Type
      GenderViaGender_id {
        Customer_gender: Code
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
      Customer_birth_date: Birth_date
      Customer_signer_name: Signer_name
      Id_typeViaSigner_id_type_id {
        Customer_signer_id_type: Name
      }
      Customer_signer_id: Signer_document
    }
    Prices: Booking_priceListViaBooking_id {
      Rent_date_day
      Rent_date_month
      Rent_date_year
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
    Booking_date_from: Date_from
    Booking_date_to: Date_to
    Booking_date_from_day: Date_from_day
    Booking_date_from_month: Date_from_month
    Booking_date_from_year: Date_from_year
    Booking_date_to_day: Date_to_day
    Booking_date_to_month: Date_to_month
    Booking_date_to_year: Date_to_year
    Booking_rent: Rent
    Booking_services: Services
    Booking_deposit: Deposit
    Booking_limit: Limit
    Booking_final_cleaning: Final_cleaning
    Booking_cleaning_freq: Cleaning_freq
    CustomerViaPayer_id {
      Customer_type: Type
      Id_typeViaId_type_id {
        Customer_id_type: Name
      }
      Customer_id: Document
      Customer_name: Name
      Customer_address: Address
      Customer_zip: Zip
      Customer_city: City
      Customer_prvince: Province
      CountryViaCountry_id {
        Customer_country: Name
      }
      Customer_email: Email
      Customer_birth_date: Birth_date
      Customer_bank_account: Bank_account
      Customer_signer_name: Signer_name
      Id_typeViaSigner_id_type_id {
        Customer_signer_id_type: Name
      }
      Customer_signer_id: Document
    }
    Rooms: Booking_roomingListViaBooking_id {
      ResourceViaResource_id {
        Resource_code: Code
        Resource_type
        Resource_part: Part
        Resource_address: Address
        Resource_street: Street
        Flat: ResourceViaFlat_id {
          Resource_flat_code: Code
          Resource_flat_address: Address
          Resource_flat_street: Street
        }
        Building: BuildingViaBuilding_id {
          Resource_building_code: Code
          Resource_building_address: Address
          SegmentViaSegment_id {
              Segment_name: Name
              Segment_url: Url
          }
          DistrictViaDistrict_id {
            LocationViaLocation_id {
              Resource_building_city: Name
            }
          }
        }
        ProviderViaOwner_id {
          Id_typeViaId_type_id {
            Owner_id_type: Name
          }
          Owner_id: Document
          Owner_name: Name
          Owner_email: Email
          Owner_address: Address
          Owner_zip: Zip
          Owner_city: City
          Owner_province: Province
          CountryViaCountry_id {
            Owner_country: Name
          }
          Owner_signers: Provider_contactListViaProvider_id (
            where: { Provider_contact_type_id: { EQ: 1 } }
          ) {
            Owner_signer: id
            Owner_signer_name: Name
            Id_typeViaId_type_id {
              Owner_signer_id_type: Name
            }
            Owner_signer_id: Document
          }
          Owner_template: Provider_templateListViaProvider_id ( where: { Active: { EQ: true }} ) { id Name Type Contract_id }
        }
        ProviderViaService_id {
          Id_typeViaId_type_id {
            Service_id_type: Name
          }
          Service_id: Document
          Service_name: Name
          Service_email: Email
          Service_address: Address
          Service_zip: Zip
          Service_city: City
          Service_province: Province
          CountryViaCountry_id {
            Service_country: Name
          }
          Service_signers: Provider_contactListViaProvider_id (
            where: { Provider_contact_type_id: { EQ: 1 } }
          ) {
            Service_signer: id
            Service_signer_name: Name
            Id_typeViaId_type_id {
              Service_signer_id_type: Name
            }
            Service_signer_id: Document
          }
          Service_template: Provider_templateListViaProvider_id ( where: { Active: { EQ: true }} ) { id Name Type Contract_id }
        }
      }
      Id_typeViaId_type_id {
        Resident_id_type: Name
      }
      Resident_id: Document
      Resident_name: Name
      Resident_address: Address
      Resident_zip: Zip
      Resident_city: City
      Resident_province: Province
      CountryViaCountry_id {
        Resident_country: Name
      }
      Resident_email: Email
    }
    Prices: Booking_group_priceListViaBooking_id {
      Rent_date_day
      Rent_date_month
      Rent_date_year
      Rent
      Services
    }
  }
}
'''


# ######################################################
# Additional functions
# ######################################################

def words(number):

  try:
    return num2words(number, lang='es')
  except:
    return ''


def age(birthdate):

  if birthdate is None or birthdate == '':
    return 18
  now = datetime.now()
  bth = datetime.strptime(birthdate, '%Y-%m-%d')
  age = now.year - bth.year
  if now.month < bth.month or (now.month == bth.month and now.day < bth.day):
      age -= 1
  return age 

def decimal (value, decimals=0):

  if value == '':
    value = 0
  return locale.format_string('%.'+str(decimals)+'f', value, grouping=True)

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

  # Locale
  locale.setlocale(locale.LC_NUMERIC, 'es_ES.UTF-8')

  # Prepare render context
  now = datetime.now()
  context['Today_day'] = now.day
  context['Today_month'] = now.month
  context['Today_year'] = now.year
  context['Server'] = 'https://' + settings.BACK + settings.API_PREFIX

  # Calculated fields
  df = datetime.strptime(context['Booking_date_from'], '%Y-%m-%d')
  dt = datetime.strptime(context['Booking_date_to'], '%Y-%m-%d')
  context['Months'] = round((dt - df).days / 30)

  # Add custom functions
  env = Environment()
  env.filters['decimal'] = decimal
  env.filters['words'] = words
  env.filters['month'] = month
  env.filters['part'] = part
  env.filters['age'] = age

  # Render contract
  text = template.replace('\r\n\r\n\r\n\r\n', '\r\n\r\n&nbsp;\r\n\r\n')
  md = env.from_string(text).render(context)

  # Convert markdown to HTML
  doc = BASE.format(markdown.markdown(md, extensions=['tables', 'attr_list']))

  # Return file
  file = BytesIO()
  html = HTML(string=doc, base_url='base_url')
  html.write_pdf(file)
  file.seek(0)

  # Render docx contract
  #doc = DocxTemplate(BytesIO(template))
  #doc.render(context, env)

  return file


# ######################################################
# Generate (rent and services) contracts
# ######################################################

def get_template(apiClient, templates, resource_type, provider):

    # No templates
    if templates is None:
      logger.warning(provider + ' no tiene plantillas de contrato')
      return None, None
   
    # Look for proper template
    fid = None
    fname = ''
    for c in templates:
      if resource_type == c['Type']:
        fid = c['Contract_id']
        fname = c['Name']
        break
    if fid is None:
      logger.warning(provider + ' no tiene plantilla de contrato de ' + resource_type)
      return None, None

    # Get template
    variables = { 'id': fid }
    q = '''
    query Contract ($id: Int) {
      data: Provider_Provider_contractList ( where: { id: { EQ: $id } } ) {
        Name
        Template
      }
    }
    '''
    result = apiClient.call(q, variables)
    template = result['data'][0]['Template']
    if template is None:
      logger.warning(provider + ' no se encuentra la plantilla de contrato de ' + resource_type)
    return template, fname
   

def do_contracts(apiClient, id):

    logger.info('Contrato para la reserva ' + str(id))

  #try:
   
    # Empty files
    json_rent = None
    json_svcs = None

    # Get booking info
    variables = { 'id': id }
    result = apiClient.call(BOOKING, variables)
    context = flatten(result['data'][0])

    # Determine template to use
    template_type = context.get('Resource_type')
    if template_type is None:
      return
    if template_type == 'plaza':
      template_type = 'habitacion'
    if context['Booking_building_type'] == 3:
      template_type = 'residencia'

    # Generate rent contract
    template, name = get_template(apiClient, context['Owner_template'], template_type, context['Owner_name'])
    if template is not None:
      file = generate_doc_file(context, template)
      response = requests.post(
        'https://' + apiClient.server + '/document/Booking/Booking/' + str(id) + '/Contract_rent/contents?access_token=' + apiClient.token,
        files={'file': file}
      )
      json_rent = { 'name': name + '.pdf', 'oid': int(response.content), 'type': 'application/pdf' }

    # Generate services contract
    if context['Owner_id'] != context['Service_id']:
      template, name = get_template(apiClient, context['Service_template'], template_type, context['Service_name'])
      if template is not None:
        file = generate_doc_file(context, template)
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
 
  #except Exception as error:
  #  logger.error(error)
  #  return False


def do_group_contracts(apiClient, id):

  logger.info('Contrato para la reserva G' + str(id))

  try:
   
    # Empty files
    json_rent = None
    json_svcs = None

    # Get booking info
    variables = { 'id': id }
    result = apiClient.call(GROUP_BOOKING, variables)
    context = flatten(result['data'][0])
    room = context['Rooms'][0]

    # Consolidate flats
    try:
      context['Flats'] = ', '.join(sorted(list({r["Resource_flat_address"] for r in context['Rooms']})))
    except:
      context['Flats'] = ', '.join(sorted(list({r["Resource_code"] for r in context['Rooms']})))

    # Generate rent contract
    template, name = get_template(apiClient, room['Owner_template'], 'grupo', room['Owner_name'])
    if template is not None:
      file = generate_doc_file(context, template)
      response = requests.post(
        'https://' + apiClient.server + '/document/Booking/Booking_group/' + str(id) + '/Contract_rent/contents?access_token=' + apiClient.token,
        files={'file': file}
      )
      json_rent = { 'name': name + '.pdf', 'oid': int(response.content), 'type': 'application/pdf' }

    # Generate services contract
    if context['Owner_id'] != context['Service_id']:
      template, name = get_template(apiClient, room['Service_template'], 'grupo', room['Service_name'])
      if template is not None:
        file = generate_doc_file(context, template)
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