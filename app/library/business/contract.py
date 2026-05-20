# ###################################################
# Imports
# ###################################################

# System includes
import io
import markdown
import requests
import locale
import base64
from pypdf import PdfWriter, PdfReader
from flask import g
from jinja2 import Environment, FileSystemLoader, select_autoescape
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Document, Signer, Tabs, SignHere, DateSigned, CustomFields, TextCustomField 
from num2words import num2words
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
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


# ######################################################
# Base template for HTML
# ######################################################

BASE = '''
<html>
<head>
<style>
@page {{ 
  size: A4; 
  margin: 1.4cm 1.4cm 1.7cm 1.4cm;
  @bottom-right {{
    margin: 0 0.2cm 1cm 0;
    content: "Pág. " counter(page);
    font-size: 14px; 
    font-family: Arial, Helvetica, sans-serif;
  }}
}}
body {{ font-size: 14px; font-weight: 400; font-family: Arial, Helvetica, sans-serif; }}
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
@media print {{
  div.keep-together {{
    break-inside: avoid;
    page-break-inside: avoid;
  }}
}}
</style>
</head>
<body>{}</body>
</html>
'''

# B2C email content
SUBJECT_B2C    = 'Contrato digital listo para firmar - ¡Tu experiencia está cerca!'
SUBJECT_B2C_EN = 'Digital contract ready to sign – Your experience is almost here!'
BODY_B2C       = '''<p>Hey!</p><p>Somos <strong>Cotown Group</strong> y queremos informarte que el <strong>contrato digital</strong> de tu reserva ya está disponible. <strong>Lee detenidamente</strong> las normas y condiciones de estancia antes de firmarlo. Una vez firmado, podremos facilitarte las llaves durante el check-in.</p><p><strong>Importante:</strong></p><p><li>Si tu llegada es <strong>fuera del horario laboral</strong>, en <strong>festivos</strong> o <strong>fin de semana</strong>, aplican condiciones especiales para el check-in. Te recomendamos coordinarlo con anticipación.</li></p><p><strong>¿Necesitas servicios adicionales?</strong> Explora opciones como traslados o limpiezas extra aquí:</p><p><a href="https://shorturl.at/w04KY">https://shorturl.at/w04KY</a></p><p>¡Quedamos atentos para resolver cualquier duda! Estamos emocionados de que disfrutes pronto de tu estancia.</p><p>Atentamente,</p><p><strong>Equipo Cotown Group</strong></p>'''
BODY_B2C_EN    = '''<p>Hey!</p><p>We’re <strong>Cotown Group</strong>, and we’re excited to let you know that the <strong>digital contract</strong> for your reservation is now ready to sign. Please take a moment to <strong>carefully review the stay rules and conditions</strong>. Once signed, we’ll be all set to hand over your keys during check-in.</p><p><strong>Important Notes:</strong></p><p><li>If you’re arriving <strong>outside business hours</strong>, on <strong>holidays</strong>, or during the <strong>weekend</strong>, special check-in conditions apply. We recommend coordinating this with us in advance.</li></p><p><strong>Need extra services?</strong> Explore options like transfers or additional cleanings here:</p><p><a href="https://shorturl.at/w04KY">https://shorturl.at/w04KY</a></p><p>Let us know if you have any questions—we’re here to help! Your amazing stay is just around the corner.</p><p>Best,</p><p><strong>The Cotown Group Team</strong></p>'''

# B2B email content
SUBJECT_B2B          = 'Contrato digital'
SUBJECT_B2B_EN       = 'Digital contract'
BODY_B2B             = ''
BODY_B2B_EN          = ''
SUBJECT_B2B_ANNEX    = 'Anexo a contrato digital'
SUBJECT_B2B_ANNEX_EN = 'Digital contract annex'
BODY_B2B_ANNEX       = ''
BODY_B2B_ANNEX_EN    = ''


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
    Booking_deposit_actual: Deposit_actual
    Booking_incasol_deposit: Incasol_deposit
    Booking_limit: Limit
    Booking_expenses: Expenses
    Booking_furniture: Furniture
    Booking_final_cleaning: Final_cleaning
    Booking_second_resident: Second_resident
    Booking_type: Book_type
    Booking_limit_type: Limit_type
    Booking_other_school: Other_school
    Booking_company: Company
    Customer_reasonViaReason_id {
      Booking_reason_id: id
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
      Resource_id: id
      Resource_code: Code
      Resource_type
      Resource_part: Part
      Resource_address: Address
      Resource_street: Street
      Resource_area: Area_woc
      Resource_registry: Registry_num 
      Resource_occupancy: Occupancy_certificate
      Resource_energy: Energy_certificate
      Resource_last_LAU_date: Last_LAU_date
      Resource_last_LAU_date_day: Last_LAU_date_day
      Resource_last_LAU_date_month: Last_LAU_date_month
      Resource_last_LAU_date_year: Last_LAU_date_year
      Resource_last_LAU_rent: Last_LAU_rent
      Flat: ResourceViaFlat_id {
        Resource_flat_id: id
        Resource_flat_code: Code
        Resource_flat_address: Address
        Resource_flat_street: Street
        Resource_flat_area: Area_woc
        Resource_flat_registry: Registry_num 
        Resource_flat_occupancy: Occupancy_certificate
        Resource_flat_energy: Energy_certificate
        Resource_flat_last_LAU_date: Last_LAU_date
        Resource_flat_last_LAU_date_day: Last_LAU_date_day
        Resource_flat_last_LAU_date_month: Last_LAU_date_month
        Resource_flat_last_LAU_date_year: Last_LAU_date_year
        Resource_flat_last_LAU_rent: Last_LAU_rent
      }
      Building: BuildingViaBuilding_id {
        Resource_building_code: Code
        Resource_building_address: Address
        Resource_building_contract: Contract
        SegmentViaSegment_id {
            Segment_name: Name
            Segment_url: Url
        }
        DistrictViaDistrict_id {
          LocationViaLocation_id {
            Resource_location_id: id
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
        Owner_template: Provider_templateListViaProvider_id ( where: { Active: { EQ: true }} ) { id Name Type Location_id Contract_id }
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
        Service_template: Provider_templateListViaProvider_id ( where: { Active: { EQ: true }} ) { id Name Type Location_id Contract_id }
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
      CountryViaNationality_id {
        Customer_nationality: Name
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
      Expenses
      Utility
      Furniture
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
    Booking_deposit_actual: Deposit_actual
    Booking_incasol_deposit: Incasol_deposit
    Booking_limit: Limit
    Booking_expenses: Expenses
    Booking_furniture: Furniture
    Booking_final_cleaning: Final_cleaning
    Booking_cleaning_freq: Cleaning_freq
    Booking_full_flat: Full_flat
    Booking_type: Book_type
    Booking_limit_type: Limit_type
    Contract_rent: Contract_rent { oid }
    Contract_services: Contract_services { oid }
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
      CountryViaNationality_id {
        Customer_nationality: Name
      }
      Customer_email: Email
      Customer_birth_date: Birth_date
      Customer_bank_account: Bank_account
      Customer_signer_name: Signer_name
      Id_typeViaSigner_id_type_id {
        Customer_signer_id_type: Name
      }
      Customer_signer_id: Signer_document
      Customer_lang: Lang
    }
    Rooms: Booking_group_roomsListViaBooking_id {
      ResourceViaResource_id {
        Resource_id: id
        Resource_code: Code
        Resource_type
        Resource_part: Part
        Resource_address: Address
        Resource_street: Street
        Resource_places: Places
        Resource_area: Area_woc
        Resource_registry: Registry_num 
        Resource_occupancy: Occupancy_certificate
        Resource_energy: Energy_certificate
        Resource_last_LAU_date: Last_LAU_date
        Resource_last_LAU_date_day: Last_LAU_date_day
        Resource_last_LAU_date_month: Last_LAU_date_month
        Resource_last_LAU_date_year: Last_LAU_date_year
        Resource_last_LAU_rent: Last_LAU_rent
        Flat: ResourceViaFlat_id {
          Resource_flat_id: id
          Resource_flat_code: Code
          Resource_flat_address: Address
          Resource_flat_street: Street
          Resource_flat_places: Places
          Resource_flat_area: Area_woc
          Resource_flat_registry: Registry_num 
          Resource_flat_occupancy: Occupancy_certificate
          Resource_flat_energy: Energy_certificate
          Resource_flat_last_LAU_date: Last_LAU_date
          Resource_flat_last_LAU_date_day: Last_LAU_date_day
          Resource_flat_last_LAU_date_month: Last_LAU_date_month
          Resource_flat_last_LAU_date_year: Last_LAU_date_year
          Resource_flat_last_LAU_rent: Last_LAU_rent
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
            Resource_location_id: id
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
        Owner_template: Provider_templateListViaProvider_id ( where: { Active: { EQ: true }} ) { id Name Type Location_id Contract_id }
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
          Service_template: Provider_templateListViaProvider_id ( where: { Active: { EQ: true }} ) { id Name Type Location_id Contract_id }
        }
      }
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

GROUP_ANNEX = '''
query Booking_group_annexById ($id: Int!, $group: String) {
  data: Booking_Booking_group_annexList (
    where: { id: { EQ: $id } }
  ) {
    Booking_groupViaBooking_id {
        Booking_id: id
        Booking_date_from: Date_from
        Booking_date_to: Date_to
        Booking_date_from_day: Date_from_day
        Booking_date_from_month: Date_from_month
        Booking_date_from_year: Date_from_year
        Booking_date_to_day: Date_to_day
        Booking_date_to_month: Date_to_month
        Booking_date_to_year: Date_to_year
        CustomerViaPayer_id {
        Customer_type: Type
        Customer_name: Name
        Customer_email: Email
        Customer_signer_name: Signer_name
        Customer_lang: Lang
        }
        Rooming: Booking_group_roomingListViaBooking_id (
        where: { 
            AND: [
            { Name: { IS_NULL: false } }
            { Group_code: { EQ: $group } }
            ] 
        }
        ) {
        Group: Group_code
        Resident_id: Document
        Resident_name: Name
        Resident_address: Address
        Resident_zip: Zip
        Resident_province: Province
        Resident_city: City
        CountryViaCountry_id {
            Resident_country: Name
        }
        Rooms: Booking_group_roomsViaRoom_id {
            ResourceViaResource_id {
              Resource_code: Code
              Resource_area: Area_woc
              Resource_occupancy: Occupancy_certificate
              Resource_energy: Energy_certificate
              BuildingViaBuilding_id {
                Building_address: Address
                DistrictViaDistrict_id {
                LocationViaLocation_id {
                  Building_city: Name
                }
              }
            }
            ProviderViaOwner_id {
              Owner_name: Name
              Owner_email: Email
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
            }
          }
        }
      }
    }
  }
}
'''

DOCUMENTS = '''
query Documents ($ids: [Int]) {
  data: Resource_ResourceList (
    where: { id: { IN: $ids } }
  ) {
    Code
    Building: BuildingViaBuilding_id {
      Building_docs: Building_docListViaBuilding_id {
        id
        Building_doc_type: Building_doc_typeViaBuilding_doc_type_id ( 
          joinType: INNER
          where: { Contract: { EQ: true } }
        ) {
          Name
        }
      }
    }
    Resource_docs: Resource_docListViaResource_id {
      id
      Resource_doc_type: Resource_doc_typeViaResource_doc_type_id ( 
        joinType: INNER
        where: { Contract: { EQ: true } }
      ) {
        Name
      }
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


# Five years ago
def five_years_ago(dt):
  if not dt:
    return True
  aux = datetime.strptime(dt, "%Y-%m-%d").date()
  return aux < date.today() - relativedelta(years=5)


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

def do_send_contract(contracts, context, type):

  # Contracts
  documents = []
  for contract in contracts:
    file = contract['file']
    if file:
      file.seek(0)
      document_base64 = base64.b64encode(file.read()).decode('utf-8')
      documents.append(
        Document(
          document_base64=document_base64,
          name=contract['name'],
          file_extension='pdf',
          document_id=str(contract['id']),
        )
      )

  # Signer
  signer = Signer(
    email=context['Customer_email'],
    name=context['Customer_name'],
    language=context['Customer_lang'] or 'es',
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
        value=type,
        show=True
      )
    ]
  )

  # Email content
  if type == 'B2C':
    subject = (SUBJECT_B2C if context['Customer_lang'] == 'es' else SUBJECT_B2C_EN) + ' (' + str(context['Booking_id']) + '-' + context['Resource_code'] + ')'
    body = BODY_B2C if context['Customer_lang'] == 'es' else BODY_B2C_EN
  elif type == 'B2B':
    subject = (SUBJECT_B2B if context['Customer_lang'] == 'es' else SUBJECT_B2B_EN) + ' (' + str(context['Booking_id']) + ')'
    body = BODY_B2B if context['Customer_lang'] == 'es' else BODY_B2B_EN
  else:
    subject = (SUBJECT_B2B_ANNEX if context['Customer_lang'] == 'es' else SUBJECT_B2B_ANNEX_EN) + ' (' + str(context['Booking_id']) + ')'
    body = BODY_B2B_ANNEX if context['Customer_lang'] == 'es' else BODY_B2B_ANNEX_EN
  
  # Envelope
  envelope_definition = EnvelopeDefinition(
    documents=documents,
    recipients={'signers': [signer]},
    email_subject=subject,
    email_blurb=body,
    custom_fields=custom_fields,
    status='sent'
  )

  # Skip sending
  logger.info(context.get('Booking_type'))
  logger.info(context.get('Resource_building_city'))
  if settings.DOCUSIGNSEND != 1 or context.get('Booking_type') or context.get('Resource_building_city') == 'Barcelona':
    logger.info('Not sent!')
    return 'n/a', 'other'
  
  # API Client setup
  api_client = ApiClient()
  api_client.set_base_path(settings.AUTHORIZATION_SERVER)
  api_client.set_oauth_host_name(settings.AUTHORIZATION_SERVER)
  
  # Private key
  private_key = get_private_key('docusign.private.key').encode('ascii').decode('utf-8')

  # Get JWT token
  token_response = get_jwt_token(private_key, settings.SCOPES, settings.AUTHORIZATION_SERVER, settings.INTEGRATION_KEY, settings.IMPERSONATED_USER_ID)
  auth=f'Bearer {token_response.access_token}'

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

def check_contracts(apiClient, id, current_status, table='Booking'):

  try:
    # API Client setup
    api_client = ApiClient()
    api_client.set_base_path(settings.AUTHORIZATION_SERVER)
    api_client.set_oauth_host_name(settings.AUTHORIZATION_SERVER)
    
    # Private key
    private_key = get_private_key('docusign.private.key').encode('ascii').decode('utf-8')

    # Get JWT token
    token_response = get_jwt_token(private_key, settings.SCOPES, settings.AUTHORIZATION_SERVER, settings.INTEGRATION_KEY, settings.IMPERSONATED_USER_ID)
    auth=f'Bearer {token_response.access_token}'

    # Get
    api_client.host = settings.ACCOUNT_BASE_URI
    api_client.set_base_path(settings.ACCOUNT_BASE_URI)
    api_client.set_default_header(header_name='Authorization', header_value=auth)
    api = EnvelopesApi(api_client)
    envelope = api.get_envelope(account_id=settings.API_ACCOUNT_ID, envelope_id=id)

    # Status
    status = envelope.status
    if status not in ('sent', 'delivered', 'declined', 'completed', 'expired'):
      status = 'other'
    
    # Datetime
    dt = str(envelope._status_changed_date_time)[:19]

    # Debug
    logger.info('Envelope: ' + envelope.envelope_id)
    logger.info('Status..: ' + current_status + ' -> ' + status)
    logger.info('Date....: ' + dt)

    # Not changed
    if status == current_status:
      return False

    # Update query
    query = '''
    mutation ($contractid: String $contractstatus: Auxiliar_Contract_statusEnumType $dt: String) {
      Booking_''' + table + '''Update (
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
  context['Today'] = now
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
  env.globals['five_years_ago'] = five_years_ago
  env.filters['decimal'] = decimal
  env.filters['words'] = words
  env.filters['month'] = month
  env.filters['part'] = part
  env.filters['age'] = age

  # Render contract
  text = template.replace('\n\n\n\n', '\n\n  \n\n')
  md = env.from_string(text).render(context)

  # Convert markdown to HTML
  doc = BASE.format(markdown.markdown(md, extensions=['md_in_html', 'tables', 'attr_list']))

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
# Merge PDF files
# ######################################################

def merge_pdfs(main_pdf, annex_files):

  main_pdf.seek(0)
  writer = PdfWriter()
  for page in PdfReader(main_pdf).pages:
    writer.add_page(page)
  for data in annex_files:
    try:
      for page in PdfReader(io.BytesIO(data)).pages:
        writer.add_page(page)
    except Exception as e:
      logger.warning('No se pudo añadir anexo al PDF: %s', e)
  out = BytesIO()
  writer.write(out)
  out.seek(0)
  return out


# ######################################################
# Fetch flat or building annexes
# ######################################################

def _unique_annexes(docs, type_key):
    seen = {}
    for doc in docs:
        doc_id = doc.get('id')
        if doc_id is None or doc_id in seen:
            continue
        name = (doc.get(type_key) or {}).get('Name')
        seen[doc_id] = {'id': doc_id, 'Name': name}
    return list(seen.values())

def fetch_annexes(apiClient, ids):
    if ids == []:
        return [], []

    result = apiClient.call(DOCUMENTS, {'ids': ids})
    if not result or not result.get('data'):
        return [], []

    entry = result['data'][0]
    building_docs = (entry.get('Building') or {}).get('Building_docs') or []
    resource_docs = entry.get('Resource_docs') or []
    building_annexes = _unique_annexes(building_docs, 'Building_doc_type')
    resource_annexes = _unique_annexes(resource_docs, 'Resource_doc_type')

    return building_annexes, resource_annexes


# ######################################################
# Generate (rent and services) contracts
# ######################################################

def get_template(apiClient, templates, resource_type, location, provider):

    # No templates
    if templates is None:
      logger.warning(provider + ' no tiene plantillas de contrato')
      return None, None, None
   
    # Look for proper template
    fid = None
    fname = ''
    dfid = None
    dfname = ''
    for c in templates:
      if c['Location_id'] == location and c['Type'] == resource_type:
        fid = c['Contract_id']
        fname = c['Name']
        break
      if c['Location_id'] == '' and c['Type'] == resource_type:
        dfid = c['Contract_id']
        dfname = c['Name']
    if (fid or dfid) is None:
      logger.warning(provider + ' no tiene plantilla de contrato de ' + resource_type)
      return None, None, None

    # Get template
    variables = { 'id': (fid or dfid) }
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
    return template, annex, (fname or dfname)
   

# ######################################################
# Generate and send B2C Contracts
# ######################################################

def do_contracts(apiClient, id):

  logger.info('Generando y enviando contrato para la reserva ' + str(id))

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

    # Get documents (solo Barcelona)
    building_documents, resource_documents = [], []
    if context.get('Resource_location_id') == 1:
      rid = context.get('Resource_flat_id') or context.get('Resource_id')
      building_documents, resource_documents = fetch_annexes(apiClient, [rid])
    annex_pairs = []
    for document in building_documents:
      data = apiClient.getFile(document['id'], 'Building/Building_doc', 'Document')
      if data and data.content:
        annex_pairs.append((document.get('Name', ''), data.content))
    for document in resource_documents:
      data = apiClient.getFile(document['id'], 'Resource/Resource_doc', 'Document')
      if data and data.content:
        annex_pairs.append((document.get('Name', ''), data.content))
    annex_pairs.sort(key=lambda x: x[0])
    annex_data = [content for _, content in annex_pairs]

    # Determine template to use
    if context['Booking_building_type'] == 3:
      template_type = 'residencia'
    elif context.get('Resource_type') in ('habitacion', 'plaza',):
      template_type = 'b2c_habitacion'
    elif context.get('Resource_type') in ('piso',):
      template_type = 'b2c_piso'
    else:
      return

    # Generate rent contract
    template, annex, name = get_template(apiClient, context['Owner_template'], template_type, context['Resource_location_id'], context['Owner_name'])
    if template is not None:
      if context['Customer_lang'] == 'en' and annex:
        template = template + '<div style="page-break-after: always;"></div>\n' + annex
      file_rent = generate_doc_file(context, template)
      if annex_data and file_rent:
        file_rent = merge_pdfs(file_rent, annex_data)
      url = 'https://' + apiClient.server + '/document/Booking/Booking/' + str(id) + '/Contract_rent/contents?access_token=' + apiClient.token
      response = requests.post(url, data=file_rent.read(), headers={ 'Content-Type': 'application/pdf' })      
      json_rent = { 'name': name + '.pdf', 'oid': int(response.content), 'type': 'application/pdf' }

    # Generate services contract
    if context['Owner_id'] != context['Service_id'] and (context['Booking_services'] or 0) > 0:
      template, annex, name = get_template(apiClient, context['Service_template'], template_type, context['Resource_location_id'], context['Service_name'])
      if template is not None:
        if context['Customer_lang'] == 'en' and annex:
          template = template + '<div style="page-break-after: always;"></div>\n' + annex
        file_svcs = generate_doc_file(context, template)
        url = 'https://' + apiClient.server + '/document/Booking/Booking/' + str(id) + '/Contract_services/contents?access_token=' + apiClient.token
        response = requests.post(url, data=file_svcs.read(), headers={ 'Content-Type': 'application/pdf' })      
        json_svcs = { 'name': name + '.pdf', 'oid': int(response.content), 'type': 'application/pdf' }

    # Send contract
    if context['Resource_building_contract']:
      contracts = [
        { 'id': 1, 'file': file_rent, 'name': 'Contrato de arrendamiento ' + str(context['Booking_id']) + ' - ' + context['Resource_code'], },
        { 'id': 2, 'file': file_svcs, 'name': 'Contrato de servicios ' + str(context['Booking_id']) + ' - ' + context['Resource_code'] }
      ]
      eid, status = do_send_contract(contracts, context, 'B2C')
    else:
      eid, status = 'n/a', 'other'

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
    if eid is not None and (json_rent is not None or json_svcs is not None):
      dt = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
      logger.info(eid + ' - ' + status + ' - ' + dt)
      result = apiClient.call(query, { 'id': id, 'contractid': eid, 'contractstatus': status, 'rent': json_rent, 'svcs': json_svcs, 'dt': dt })
      return True
    return False
 
  except Exception as error:
    logger.error(error)
    import traceback
    traceback.print_exc()

    return False


# ######################################################
# Generate B2B Contracts
# ######################################################

def do_group_contracts(apiClient, id):

  logger.info('Generando contrato para la reserva G' + str(id))

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
    flats_dict = {}
    for room in context['Rooms']:
      code = room.get('Resource_flat_code')
      if code and len(code) == 12:
        flats_dict[code] = {
          k.replace('_flat_', '_'): v for k, v in room.items() if k.startswith('Resource_flat_')
        }
      code = room.get('Resource_code')
      if code and len(code) == 12:
        flats_dict[code] = {
          k: v for k, v in room.items() if k.startswith('Resource_')
        }
    context['Flats_info'] = list(flats_dict.values())
    context['Flats'] = ', '.join(sorted(f['Resource_address'] for f in context['Flats_info']))

    # Get documents (solo Barcelona)
    building_documents, resource_documents = [], []
    if context.get('Rooms')[0].get('Resource_location_id') == 1:
      rids = [r.get('Resource_flat_id') or r.get('Resource_id') for r in context.get('Rooms')]
      building_documents, resource_documents = fetch_annexes(apiClient, rids)
    annex_pairs = []
    for document in building_documents:
      data = apiClient.getFile(document['id'], 'Building/Building_doc', 'Document')
      if data and data.content:
        annex_pairs.append((document.get('Name', ''), data.content))
    for document in resource_documents:
      data = apiClient.getFile(document['id'], 'Resource/Resource_doc', 'Document')
      if data and data.content:
        annex_pairs.append((document.get('Name', ''), data.content))
    annex_pairs.sort(key=lambda x: x[0])
    annex_data = [content for _, content in annex_pairs]

    # Determine template to use
    template_type = 'b2b_habitacion'
    if context.get('Booking_full_flat'):
      template_type = 'b2b_piso'
    
    # Generate rent contract
    template, annex, name = get_template(apiClient, room['Owner_template'], template_type, room['Resource_location_id'], room['Owner_name'])
    if template is not None:
      file_rent = generate_doc_file(context, template)
      if annex_data and file_rent:
        file_rent = merge_pdfs(file_rent, annex_data)
      url = 'https://' + apiClient.server + '/document/Booking/Booking_group/' + str(id) + '/Contract_rent/contents?access_token=' + apiClient.token
      response = requests.post(url, data=file_rent.read(), headers={ 'Content-Type': 'application/pdf' })      
      json_rent = { 'name': name + '.pdf', 'oid': int(response.content), 'type': 'application/pdf' }

    # Generate services contract
    if room['Owner_id'] != room['Service_id'] and (context['Booking_services'] or 0) > 0:
      template, annex, name = get_template(apiClient, room['Service_template'], template_type, room['Resource_location_id'], room['Service_name'])
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
    import traceback
    traceback.print_exception(error)
    logger.error(error)
    import prints
    return False


# ######################################################
# Send B2B Contracts
# ######################################################

def send_group_contracts(apiClient, id):

  logger.info('Enviando contrato para la reserva G' + str(id))

  try:

    # Get booking info
    variables = { 'id': id }
    result = apiClient.call(GROUP_BOOKING, variables)
    context = flatten(result['data'][0])

    # Get contracts
    file_rent = apiClient.getFile(id, 'Booking/Booking_group', 'Contract_rent')
    file_r = io.BytesIO(file_rent.content) if file_rent.content else None
    file_s = None
    if not context.get('Contract_services') == None:
      logger.info('Contrato de servicios no encontrado')
    else:
      file_svcs = apiClient.getFile(id, 'Booking/Booking_group', 'Contract_services')
      file_s = io.BytesIO(file_svcs.content) if file_svcs.content else None

    # Send contracts
    contracts = [
      { 'id': 1, 'file': file_r, 'name': 'Contrato de arrendamiento ' + str(context['Booking_id']) },
      { 'id': 2, 'file': file_s, 'name': 'Contrato de servicios ' + str(context['Booking_id']) } 
    ]
    eid, status = do_send_contract(contracts, context, 'B2B')

    # Update query
    query = '''
    mutation ($id: Int! $contractid: String $contractstatus: Auxiliar_Contract_statusEnumType $dt: String) {
      Booking_Booking_groupUpdate (
        where:  { id: {EQ: $id} }
        entity: {
          Contract_id: $contractid
          Contract_status: $contractstatus
          Contract_signed: $dt
        }
      ) { id }
    }
    '''

    # Call graphQL endpoint
    dt = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
    if eid:
      logger.info(eid + ' - ' + status + ' - ' + dt)
      apiClient.call(query, { 'id': id, 'contractid': eid, 'contractstatus': status, 'dt': dt })
    return True
 
  except Exception as error:
    logger.error(error)
    return False


# ######################################################
# Generate and send B2B Annexes
# ######################################################

def do_group_annexes(apiClient, id, code):

  try:

    # Get booking info
    variables = { 'id': id, 'group': code }
    result = apiClient.call(GROUP_ANNEX, variables)
    context = flatten(result['data'][0])
    name = str(context['Booking_id']) + '-' + code
    logger.info('Generando y enviando anexo para la reserva G' + name)
    if not context['Rooming']:
      logger.warning('Rooming vacía!')
      return False

    # Jinja environment
    env = Environment(
      loader=FileSystemLoader('./templates/other'),
      autoescape=select_autoescape(['html', 'xml'])
    )

    # Generate HTML
    context['Server'] = 'https://' + settings.BACK + settings.API_PREFIX
    tpl = env.get_template('annex.html')
    result = tpl.render(context)

    # Generate PDF
    file_annex = BytesIO()
    html = HTML(string=result)
    html.write_pdf(file_annex)
    file_annex.seek(0)

    # Upload pdf
    url = 'https://' + apiClient.server + '/document/Booking/Booking_group_annex/' + str(id) + '/Contract_annex/contents?access_token=' + apiClient.token
    response = requests.post(url, data=file_annex.read(), headers={ 'Content-Type': 'application/pdf' })      
    json_annex = { 'name': name + '.pdf', 'oid': int(response.content), 'type': 'application/pdf' }

    # Send contracts
    contracts = [
      { 'id': 1, 'file': file_annex, 'name': 'Anexo al contrato - Reserva ' + str(context['Booking_id']) },
    ]
    eid, status = do_send_contract(contracts, context, 'B2B Anexo')

    # Update query
    query = '''
    mutation ($id: Int! $contractid: String $contractstatus: Auxiliar_Contract_statusEnumType $annex: Models_DocumentTypeInputType $dt: String) {
      Booking_Booking_group_annexUpdate (
        where:  { id: {EQ: $id} }
        entity: {
          Contract_id: $contractid
          Contract_status: $contractstatus
          Contract_annex: $annex
          Contract_signed: $dt
        }
      ) { id }
    }
    '''

    # Call graphQL endpoint
    if file_annex is not None:
      dt = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
      apiClient.call(query, { 'id': id, 'contractid': eid, 'contractstatus': status, 'annex': json_annex, 'dt': dt })
      return True
    
    # Error
    return False

  except Exception as error:
    logger.error(error)
    import traceback
    traceback.print_exc()
    return False