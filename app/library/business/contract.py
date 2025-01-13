# ###################################################
# Imports
# ###################################################

# System includes
import markdown
import requests
import locale
import base64
from flask import g
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Document, Signer, Tabs, SignHere, DateSigned, CustomFields, TextCustomField 
from num2words import num2words
from datetime import datetime
from jinja2 import Environment
from weasyprint import HTML
from io import BytesIO
from os import path

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Cotown includes
from library.services.config import settings
from library.services.utils import flatten
from library.business.queries import q_change_contract


# ######################################################
# Base template for HTML
# ######################################################

BASE = '''
<html>
<head>
<style>
@page {{ size: A4; margin: 1.4cm; }}
body {{ font-size: 14px; font-weight: 400; font-family: Arial, Helvetica, sans-serif;
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
.signature {{ padding: 20px 0px; color: white; }}
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
        Owner_bill_line: Bill_line
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
      Customer_lang: Lang
    }
    Residents: Booking_roomingListViaBooking_id {
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
    }
    Prices: Booking_priceListViaBooking_id (
        orderBy: [{ attribute: Rent_date }]
      ) {
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
      Customer_signer_id: Signer_document
    }
    Rooms: Booking_group_roomingListViaBooking_id {
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
    Prices: Booking_group_priceListViaBooking_id (
        orderBy: [{ attribute: Rent_date }]
      ) {
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

# Convert number to words
def words(number):

  try:
    return num2words(number, lang='es')
  except:
    return ''


# Calc current age
def age(birthdate):

  if birthdate is None or birthdate == '':
    return 18
  now = datetime.now()
  bth = datetime.strptime(birthdate, '%Y-%m-%d')
  age = now.year - bth.year
  if now.month < bth.month or (now.month == bth.month and now.day < bth.day):
      age -= 1
  return age 


# Convert to number to words
def decimal (value, decimals=0):

  if value == '':
    value = 0
  return locale.format_string('%.'+str(decimals)+'f', value, grouping=True)


# Get month name
def month(m, lang='es'):

  try:
    if lang == 'es':
      return ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'][m-1]
    else:
      return ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][m-1]
  except:
    return '--'


# Get part in words
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


# Get Docusign JWT token
def get_jwt_token(private_key, scopes, auth_server, client_id, impersonated_user_id):
  '''Get the jwt token'''
  api_client = ApiClient()
  api_client.set_base_path(auth_server)
  response = api_client.request_jwt_user_token(
    client_id=client_id,
    user_id=impersonated_user_id,
    oauth_host_name=auth_server,
    private_key_bytes=private_key,
    expires_in=4000,
    scopes=scopes
  )
  return response


# Get Docusign private key
def get_private_key(private_key_path):
  private_key_file = path.abspath(private_key_path)
  if path.isfile(private_key_file):
    with open(private_key_file) as private_key_file:
      private_key = private_key_file.read()
  else:
    private_key = private_key_path
  return private_key


# ######################################################
# Send documents to sign
# ######################################################

def do_send_contract(file_rent, file_svcs, context):

  # API Client setup
  api_client = ApiClient()
  api_client.set_base_path(settings.AUTHORIZATION_SERVER)
  api_client.set_oauth_host_name(settings.AUTHORIZATION_SERVER)
  
  # Private key
  private_key = get_private_key('docusign.private.key').encode('ascii').decode('utf-8')

  # Get JWT token
  token_response = get_jwt_token(private_key, settings.SCOPES, settings.AUTHORIZATION_SERVER, settings.INTEGRATION_KEY, settings.IMPERSONATED_USER_ID)
  auth=f'Bearer {token_response.access_token}'

  # Rent contract
  documents = []
  file_rent.seek(0)
  document_base64 = base64.b64encode(file_rent.read()).decode('utf-8')
  documents.append(
    Document(
      document_base64=document_base64,
      # TO DO: Nombre del documento
      name='Contrato de arrendamiento ' + str(context['Booking_id']) + ' - ' + context['Resource_code'],
      file_extension='pdf',
      document_id='1',
    )
  )

  # Services contract
  if file_svcs:
    file_svcs.seek(0)
    document_base64 = base64.b64encode(file_svcs.read()).decode('utf-8')
    documents.append(
      Document(
        document_base64=document_base64,
        # TO DO: Nombre del documento
        name='Contrato de servicios ' + str(context['Booking_id']) + ' - ' + context['Resource_code'],
        file_extension='pdf',
        document_id='2',
      )
    )

  # Signer
  signer = Signer(
    #?email=context['Customer_email'],
    email='dalarcon@cotown.com',
    name=context['Customer_name'],
    language='es',
    recipient_id='1',
    tabs=Tabs(
      sign_here_tabs=[
        SignHere(anchor_string='/FIRMACLIENTE/')
      ],
      date_signed_tabs=[
        DateSigned(anchor_string='/FECHACLIENTE/')
      ]
    )
  )

  # Custom fields - Create first in Admin
  custom_fields = CustomFields(
    text_custom_fields=[
      TextCustomField(
        name='Booking Id',
        value=context['Booking_id'],
        show=True
      ),
      TextCustomField(
        name='Booking Type',
        value='B2C',
        show=True
      )
    ]
  )

  # Envelope
  envelope_definition = EnvelopeDefinition(
    documents=documents,
    recipients={'signers': [signer]},
    email_subject='Contrato(s)  ' + str(context['Booking_id']) + ' - ' + context['Resource_code'],
    email_blurb='BODY',
    custom_fields=custom_fields,
    status='sent'
  )

  # Send
  api_client.host = settings.ACCOUNT_BASE_URI
  api_client.set_base_path(settings.ACCOUNT_BASE_URI)
  api_client.set_default_header(header_name='Authorization', header_value=auth)
  api = EnvelopesApi(api_client)
  summary = api.create_envelope(account_id=settings.API_ACCOUNT_ID, envelope_definition=envelope_definition)

  # Result
  return summary.envelope_id, summary.status


# ######################################################
# Send documents to sign
# ######################################################

def check_contracts(apiClient, id, current_status):

  try:
    # API Client setup
    api_client = ApiClient()
    api_client.set_base_path(settings.AUTHORIZATION_SERVER)
    api_client.set_oauth_host_name(settings.AUTHORIZATION_SERVER)
    
    # Private key
    private_key = get_private_key('test.private.key').encode('ascii').decode('utf-8')

    # Get JWT token
    token_response = get_jwt_token(private_key, settings.SCOPES, settings.AUTHORIZATION_SERVER, settings.INTEGRATION_KEY, settings.IMPERSONATED_USER_ID)
    auth=f'Bearer {token_response.access_token}'

    # Get
    api_client.host = settings.ACCOUNT_BASE_URI
    api_client.set_base_path(settings.ACCOUNT_BASE_URI)
    api_client.set_default_header(header_name='Authorization', header_value=auth)
    api = EnvelopesApi(api_client)
    envelope = api.get_envelope(account_id=settings.API_ACCOUNT_ID, envelope_id=id)

    # Status changed
    status = envelope.status
    if status not in ('sent', 'delivered', 'declined', 'completed', 'expired'):
      status = 'other'
    if status == current_status:
      return False
    
    # Datetime
    dt = str(envelope._status_changed_date_time)[:19]

    # Debug
    logger.info("Envelope: " + envelope.envelope_id)
    logger.info("Status..: " + current_status + ' -> ' + status)
    logger.info("Date....: " + dt)

    # Update query
    query = '''
    mutation ($contractid: String $contractstatus: Auxiliar_Contract_statusEnumType $dt: String) {
      Booking_BookingUpdate (
        where:  { Contract_id: {EQ: $contractid} }
        entity: {
          Contract_status: $contractstatus
          Contract_signed: $dt
        }
      ) { id }
    }
    '''

    # Call graphQL endpoint
    apiClient.call(query, { 'contractid': id, 'contractstatus': status, 'dt': dt })
    return True

  # Error
  except Exception as error:
    logger.error(error)
    return False


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
  text = template.replace('\n\n\n\n', '\n\n  \n\n')
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
      return None, None, None
   
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
      return None, None, None

    # Get template
    variables = { 'id': fid }
    q = '''
    query Contract ($id: Int) {
      data: Provider_Provider_contractList ( where: { id: { EQ: $id } } ) {
        Name
        Template
        Annex
      }
    }
    '''
    result = apiClient.call(q, variables)
    template = result['data'][0]['Template']
    annex = result['data'][0]['Annex']
    if template is None:
      logger.warning(provider + ' no se encuentra la plantilla de contrato de ' + resource_type)
    return template, annex, fname
   

def do_contracts(apiClient, id):

  logger.info('Contrato para la reserva ' + str(id))

  try:
   
    # Empty files
    file_rent = None
    file_svcs = None
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
    template, annex, name = get_template(apiClient, context['Owner_template'], template_type, context['Owner_name'])
    if template is not None:
      if context['Customer_lang'] == 'en' and annex:
        template = template + '<div style="page-break-after: always;"></div>\n' + annex
      file_rent = generate_doc_file(context, template)
      url = 'https://' + apiClient.server + '/document/Booking/Booking/' + str(id) + '/Contract_rent/contents?access_token=' + apiClient.token
      response = requests.post(url, data=file_rent.read(), headers={ 'Content-Type': 'application/pdf' })      
      json_rent = { 'name': name + '.pdf', 'oid': int(response.content), 'type': 'application/pdf' }

    # Generate services contract
    if context['Owner_id'] != context['Service_id'] and context['Booking_services'] > 0:
      template, annex, name = get_template(apiClient, context['Service_template'], template_type, context['Service_name'])
      if template is not None:
        if context['Customer_lang'] == 'en' and annex:
          template = template + '<div style="page-break-after: always;"></div>\n' + annex
        file_svcs = generate_doc_file(context, template)
        url = 'https://' + apiClient.server + '/document/Booking/Booking/' + str(id) + '/Contract_services/contents?access_token=' + apiClient.token
        response = requests.post(url, data=file_svcs.read(), headers={ 'Content-Type': 'application/pdf' })      
        json_svcs = { 'name': name + '.pdf', 'oid': int(response.content), 'type': 'application/pdf' }

    # Send contract
    eid, status = do_send_contract(file_rent, file_svcs, context)
    #?eid, status = 'n/a', 'sent'

    # Update query
    query = '''
    mutation ($id: Int! $contractid: String $contractstatus: Auxiliar_Contract_statusEnumType $rent: Models_DocumentTypeInputType $svcs: Models_DocumentTypeInputType $dt: String) {
      Booking_BookingUpdate (
        where:  { id: {EQ: $id} }
        entity: {
          Contract_id: $contractid
          Contract_status: $contractstatus
          Contract_rent: $rent
          Contract_services: $svcs
          Contract_signed: $dt
        }
      ) { id }
    }
    '''

    # Call graphQL endpoint
    if json_rent is not None or json_svcs is not None:
      dt = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
      logger.info(eid + ' - ' + status + ' - ' + dt)
      apiClient.call(query, { 'id': id, 'contractid': eid, 'contractstatus': status, 'rent': json_rent, 'svcs': json_svcs, 'dt': dt })
      return True
    return False
 
  except Exception as error:
    logger.error(error)
    return False


def do_group_contracts(apiClient, id):

  logger.info('Contrato para la reserva G' + str(id))

  try:

    # Empty files
    file_rent = None
    file_svcs = None
    json_rent = None
    json_svcs = None
    
    # Empty files
    json_rent = None
    json_svcs = None

    # Get booking info
    variables = { 'id': id }
    result = apiClient.call(GROUP_BOOKING, variables)
    context = flatten(result['data'][0])
    if not context['Rooms']:
      return False
    room = context['Rooms'][0]

    # Consolidate flats
    try:
      context['Flats'] = ', '.join(sorted(list({r["Resource_flat_address"] for r in context['Rooms']})))
    except:
      context['Flats'] = ', '.join(sorted(list({r["Resource_code"] for r in context['Rooms']})))

    # Generate rent contract
    template, annex, name = get_template(apiClient, room['Owner_template'], 'grupo', room['Owner_name'])
    if template is not None:
      file_rent = generate_doc_file(context, template)
      url = 'https://' + apiClient.server + '/document/Booking/Booking_group/' + str(id) + '/Contract_rent/contents?access_token=' + apiClient.token
      response = requests.post(url, data=file_rent.read(), headers={ 'Content-Type': 'application/pdf' })      
      json_rent = { 'name': name + '.pdf', 'oid': int(response.content), 'type': 'application/pdf' }

    # Generate services contract
    if room['Owner_id'] != room['Service_id']:
      template, annex, name = get_template(apiClient, room['Service_template'], 'grupo', room['Service_name'])
      if template is not None:
        file_svcs = generate_doc_file(context, template)
        url = 'https://' + apiClient.server + '/document/Booking/Booking_group/' + str(id) + '/Contract_services/contents?access_token=' + apiClient.token
        response = requests.post(url, data=file_svcs.read(), headers={ 'Content-Type': 'application/pdf' })      
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