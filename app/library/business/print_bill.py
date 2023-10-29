# ######################################################
# Imports
# ######################################################

# System includes
import requests
import logging
from io import BytesIO
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Cotown includes
from library.services.utils import flatten


# ######################################################
# Query to retrieve the bill
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
       Booking_groupViaBooking_group_id {
           BuildingViaBuilding_id {
               Building_code: Code
           }
       }
       Bill_code: Code
       Bill_concept: Concept
       Issued
       Bill_issued_date: Issued_date
       Bill_total: Total
       CustomerViaCustomer_id {
           Customer_id: Document
           Customer_name: Name
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
           Provider_bill_line: Bill_line
           CountryViaCountry_id {
               Provider_country: Name
           }
       }
       Lines: Invoice_lineListViaInvoice_id {
           Line_concept: Concept
           Line_comments: Comments
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
# Format date
# ######################################################

def ymd(v):

 return v[8:10] + '/' + v[5:7] + '/' + v[:4]


# ######################################################
# Generate file
# ######################################################

def generate_bill_file(context):

 # Jinja environment
 env = Environment(
   loader=FileSystemLoader('./templates/other'),
   autoescape=select_autoescape(['html', 'xml'])
 )
 env.filters['ymd'] = ymd

 # Generate HTML
 tpl = env.get_template('bill.html')
 result = tpl.render(context)

 # Generate PDF
 file = BytesIO()
 html = HTML(string=result)
 html.write_pdf(file)
 file.seek(0)
 return file


# ######################################################
# Generate bill
# ######################################################

def do_bill(apiClient, id):

 try:

   # Get bill info
   variables = { 'id': id }
   result = apiClient.call(BILL, variables)
   context = flatten(result['data'][0])

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
   file = generate_bill_file(context)
   response = requests.post(
     'https://' + apiClient.server + '/document/Billing/Invoice/' + str(id) + '/Document/contents?access_token=' + apiClient.token, 
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
       'name': str(context['Bill_type']).capitalize() + ' ' + str(context['Bill_code']) + '.pdf', 
       'oid': int(oid), 
       'type': 'application/pdf' 
     }
   }

   # Call graphQL endpoint
   apiClient.call(query, variables)
   return True
 
 except Exception as error:
   logger.error(error)
   return False
