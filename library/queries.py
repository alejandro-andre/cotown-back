# ######################################################
# Imports
# ######################################################

# System includes
import requests


# ######################################################
# Query to retrieve customer
# ######################################################

CUSTOMER = '''
query CustomerById ($id: Int!) {
    data: Customer_CustomerList (
        where: { id: { EQ: $id }}
    ) { 
        Name
        Last_name
        Email
        Document
        User_name
    }
}'''


# ######################################################
# Get customer
# ######################################################

def get_customer(apiClient, id):

  try:
    variables = { 'id': id }
    result = apiClient.call(CUSTOMER, variables)['data']
    return result[0] if len(result) > 0 else None

  except Exception as error:
    print(error)
    return None
