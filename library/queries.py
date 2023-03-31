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
    dbClient.connect()
    dbClient.select('SELECT id, "Name", "Last_name", "Email", "Document", "User_name" FROM "Provider"."Provider" WHERE id=%s', (id,))
    aux = dbClient.fetch()
    dbClient.disconnect()
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
    dbClient.connect()
    dbClient.select('SELECT id, "Name", "Last_name", "Email", "Document", "User_name" FROM "Customer"."Customer" WHERE id=%s', (id,))
    aux = dbClient.fetch()
    dbClient.disconnect()
    print(aux)
    return aux

  except Exception as error:
    print(error)
    return None


# ######################################################
# Availability
# ######################################################

def availability(dbClient, date_from, date_to, place_type):

  try:
    dbClient.connect()
    dbClient.select('''
    SELECT r."Code"
    FROM "Resource"."Resource" r
    INNER JOIN "Resource"."Resource_place_type" t ON t.id = r."Place_type_id" 
    LEFT JOIN "Booking"."Booking_detail" b ON r.id = b."Booking_id" 
    AND b."Date_from" <= %s 
    AND b."Date_to" >= %s
    WHERE b.id IS NULL 
    AND t."Code" LIKE %s
    ORDER BY r."Code";''', (date_from, date_to, place_type + '%'))
    aux = dbClient.fetchall()
    dbClient.disconnect()
    list = [item for sub_list in aux for item in sub_list]
    return list

  except Exception as error:
    print(error)
    return None
