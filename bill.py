# ###################################################
# Imports
# ###################################################

# System includes
import requests
import os

# Cotown includes
from library.dbclient import DBClient
from library.apiclient import APIClient
from library.utils import flatten_json
from library.generate_bill import generate_bill


# ######################################################
# Query
# ######################################################

BILL = '''
query BillById ($id: Int!) {
    data: Billing_InvoiceList (
        where: { 
            AND: [
                { id: { EQ: $id }},
                { Issued: { EQ: true }}
            ]
        }
    ) { 
        Bill_type
        BookingViaBooking_id {
            ResourceViaResource_id {
                Resource_code: Code
            }
        }
        Bill_code: Code
        Bill_details: Details
        Issued
        Bill_issue_date: Issue_date
        Bill_total: Total
        CustomerViaCustomer_id {
            Customer_id: Document
            Customer_name: Name
            Customer_last_name: Last_name
            Customer_address: Address
            Customer_zip: Zip
            Customer_city: City
            CountryViaCountry_id {
                Customer_country: Name
            }
        }
        ProviderViaProvider_id {
            Provider_id: Document
            Provider_name: Name
            Provider_address: Address
            Provider_zip: Zip
            Provider_city: City
            CountryViaCountry_id {
                Provider_country: Name
            }
        }
        Lines: Invoice_lineListViaInvoice_id {
            Line_details: Details
            ProductViaProduct_id {
                Line_product: Name
            }
            TaxViaTax_id {
                Line_tax_name: Name
                Line_tax_value: Value
            }
            Line_amount: Amount
        }
    }
}'''


# ######################################################
# Generate bill
# ######################################################

def do_bill(apiClient, id):

  # Get bill info
  variables = { 'id': id }
  result = apiClient.call(BILL, variables)
  context = flatten_json(result['data'][0])

  # Aggregate taxes
  taxes = {}
  for line in context['Lines']:
    amount    = line['Line_amount']
    tax_name  = line['Line_tax_name']
    tax_value = line['Line_tax_value']
    tax_line  = taxes.get(tax_name)
    if tax_line is None:
       taxes[tax_name] = { 'Amount': amount, 'Tax_name': tax_name, 'Tax_value': tax_value }
    else:
       taxes[tax_name]['Amount'] += amount
  for tax in taxes:
     taxes[tax]['Base'] = taxes[tax]['Amount'] / (1 + taxes[tax]['Tax_value'] / 100)
     taxes[tax]['Tax'] = taxes[tax]['Amount'] - taxes[tax]['Base']
  context['Taxes'] = list(taxes.values())

  # Generate rent contract
  file = generate_bill(context, 'templates/bill.html')
  response = requests.post(
    'https://experis.flows.ninja/document/Billing/Invoice/' + str(id) + '/Document/contents?access_token=' + apiClient.token, 
    files={'file': file}
  )
  oid = response.content

  # Update query
  query = '''
  mutation ($id: Int! $bill: Models_DocumentTypeInputType) {
    Billing_InvoiceUpdate (
      where:  { id: {EQ: $id} }
      entity: { 
        Document: $bill 
      }
    ) { id }
  }
  '''

  # Update variables
  variables = {
    'id': id, 
    'bill': { 
      'name': 'factura.pdf', 
      'oid': int(oid), 
      'type': 'application/pdf' 
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

    # Get pending billis
    bills = apiClient.call('''
    {
      data: Billing_InvoiceList ( 
        where: { 
          AND: [
            { Issued: { EQ: true } }, 
            { Document: { IS_NULL: false } } 
          ] 
        }
      ) { id }
    }
    ''')

    # Loop thru contracts
    if bills  is not None:
      for b in bills.get('data'):
          id = b['id']
          print(id)
          do_bill(apiClient, id)


# #####################################
# Main
# #####################################

if __name__ == '__main__':

    main()