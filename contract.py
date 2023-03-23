# ###################################################
# Imports
# ###################################################

# System includes
from openpyxl import load_workbook
import requests
import os

# Cotown includes
from library.dbclient import DBClient
from library.apiclient import APIClient
from library.utils import flatten_json
from library.generate_doc import generate_doc


# ######################################################
# Query
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
        Owner_template: Provider_templateListViaProvider_id ( where: { Active: { EQ: true }} ) { id }
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
        Service_template: Provider_templateListViaProvider_id ( where: { Active: { EQ: true }} ) { id }
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
# Generate contract
# ######################################################

def do_contracts(apiClient, id):

  # Get booking info
  variables = { 'id': id }
  result = apiClient.call(BOOKING, variables)
  context = flatten_json(result['data'][0])

  # Get rent template
  if context.get('Owner_template') is None:
    print(context['Owner_name'], 'no tiene plantilla de contrato de renta')
    return
  fid = context['Owner_template'][0]['id']
  template = apiClient.getFile(fid, 'Provider/Provider_template', 'Template')
  if template is None:
    print(context['Owner_name'], 'no tiene plantilla de contrato de renta')
    return

  # Generate rent contract
  file = generate_doc(context, template.content)
  response = requests.post(
    'https://experis.flows.ninja/document/Booking/Booking/' + str(id) + '/Contract_rent/contents?access_token=' + apiClient.token, 
    files={'file': file}
  )
  oid_rent = response.content

  # Get services template
  if context.get('Service_template') is None:
    print(context['Owner_name'], 'no tiene plantilla de contrato de servicios')
    return
  fid = context['Service_template'][0]['id']
  template = apiClient.getFile(fid, 'Provider/Provider_template', 'Template')
  if template is None:
    print(context['Owner_name'], 'no tiene plantilla de contrato de servicios')
    return

  # Generate services contract
  file = generate_doc(context, template.content)
  response = requests.post(
    'https://experis.flows.ninja/document/Booking/Booking/' + str(id) + '/Contract_services/contents?access_token=' + apiClient.token, 
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
  return ('ok!')


# ###################################################
# Contract generator function
# ###################################################

def main():

    # ###################################################
    # Environment variables
    # ###################################################

    SERVER   = str(os.environ.get('COTOWN_SERVER'))
    DATABASE = str(os.environ.get('COTOWN_DATABASE'))
    DBUSER   = str(os.environ.get('COTOWN_DBUSER'))
    DBPASS   = str(os.environ.get('COTOWN_DBPASS'))
    GQLUSER  = str(os.environ.get('COTOWN_GQLUSER'))
    GQLPASS  = str(os.environ.get('COTOWN_GQLPASS'))
    SSHUSER  = str(os.environ.get('COTOWN_SSHUSER'))
    SSHPASS  = str(os.environ.get('COTOWN_SSHPASS'))

    # Test
    SERVER   = 'experis.flows.ninja'
    DATABASE = 'niledb'
    DBUSER   = 'postgres'
    DBPASS   = 'postgres'
    GQLUSER  = 'modelsadmin'
    GQLPASS  = 'Ciber$2022'
    SSHUSER  = 'themes'
    SSHPASS  = 'Admin1234!'


    # ###################################################
    # GraphQL and DB client
    # ###################################################

    # graphQL API
    apiClient = APIClient(SERVER)
    apiClient.auth(user=GQLUSER, password=GQLPASS)

    # DB API
    dbClient = DBClient(SERVER, DATABASE, DBUSER, DBPASS, SSHUSER, SSHPASS)
    dbClient.connect()


    # ###################################################
    # Main
    # ###################################################

    # Get pending contracts
    bookings = apiClient.call('''
    {
      data: Booking_BookingList ( 
        orderBy: [{ attribute: id }]
        where: { 
          AND: [
            { Status: { EQ: confirmada } }, 
            { Contract_rent: { IS_NULL: true } } 
          ] 
        }
      ) { id }
    }
    ''')

    # Loop thru contracts
    if bookings is not None:
      for booking in bookings.get('data'):
          id = booking['id']
          print(id)
          do_contracts(apiClient, id)


# #####################################
# Main
# #####################################

if __name__ == '__main__':

    main()