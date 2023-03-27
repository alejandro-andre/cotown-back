# ######################################################
# Imports
# ######################################################

# System includes
import requests


# ######################################################
# Get provider
# ######################################################

def get_provider(dbClient, id):

  try:
    dbClient.select('SELECT id, "Name", "Last_name", "Email", "Document", "User_name" FROM "Provider"."Provider" WHERE id=%s', (id,))
    aux = dbClient.fetch()
    print(aux)
    return aux

  except Exception as error:
    print(error)
    return None


# ######################################################
# Get customer
# ######################################################

def get_customer(dbClient, id):

  try:
    dbClient.select('SELECT id, "Name", "Last_name", "Email", "Document", "User_name" FROM "Customer"."Customer" WHERE id=%s', (id,))
    aux = dbClient.fetch()
    print(aux)
    return aux

  except Exception as error:
    print(error)
    return None
