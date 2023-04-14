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
# Generate file
# ######################################################

def generate_email(context, template):

  # Jinja environment
  env = Environment(
      loader=FileSystemLoader('./email'),
      autoescape=select_autoescape(['html', 'xml'])
  )

  # Generate HTML
  tpl = env.get_template(template)
  return tpl.render(data=context)


# ######################################################
# Generate bill
# ######################################################

def do_email(apiClient, id):

    return True
