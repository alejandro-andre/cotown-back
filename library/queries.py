# ######################################################
# Imports
# ######################################################

# System includes
import requests


# ######################################################
# Get provider
# ######################################################

def get_provider(apiClient, id):

  query = '''
  query ProviderById ($id: Int!) {
      data: Provider_ProviderList (
          where: { id: { EQ: $id }}
      ) { 
          Name
          Last_name
          Email
          Document
          User_name
      }
  }'''

  try:
    variables = { 'id': id }
    result = apiClient.call(query, variables)['data']
    return result[0] if len(result) > 0 else None

  except Exception as error:
    print(error)
    return None


# ######################################################
# Get customer
# ######################################################

def get_customer(apiClient, id):

  query = '''
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

  try:
    variables = { 'id': id }
    result = apiClient.call(query, variables)['data']
    return result[0] if len(result) > 0 else None

  except Exception as error:
    print(error)
    return None
