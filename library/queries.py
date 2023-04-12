# ######################################################
# Imports
# ######################################################

# System includes
import datetime


# ######################################################
# Get payment
# ######################################################

def get_payment(dbClient, id):

  try:
    # Get payment
    dbClient.connect()
    dbClient.select('SELECT id, "Issued_date", "Concept", "Amount" FROM "Billing"."Payment" WHERE id=%s', (id,))
    aux = dict(dbClient.fetch())
    aux['Issued_date'] = aux['Issued_date'].strftime("%Y-%m-%d")

    # Get order num
    dbClient.select('SELECT nextval(\'"Auxiliar"."Secuence_Payment_order_seq"\')')
    val = dbClient.fetch()
    order = "{:04d}CT{:06d}".format(datetime.datetime.now().year, val[0])
    aux['Order'] = order

    # Update payment
    dbClient.execute('UPDATE "Billing"."Payment" SET "Order_num"=%s', (order,))
    dbClient.commit()
    dbClient.disconnect()

    # Prepare response
    print(aux)
    return aux

  except Exception as error:
    print(error)
    return None


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

def availability(dbClient, date_from, date_to, building, place_type):

  if building is None:
    building = ''

  if place_type is None:
    place_type = ''
    
  try:
    dbClient.connect()
    dbClient.select('''
    SELECT r."Code"
    FROM "Resource"."Resource" r
    INNER JOIN "Building"."Building" b ON b.id = r."Building_id" 
    INNER JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id" 
    LEFT JOIN "Booking"."Booking_detail" bd ON bd."Resource_id" = r.id 
    AND bd."Date_from" <= %s 
    AND bd."Date_to" >= %s
    WHERE bd.id IS NULL 
    AND rpt."Code" LIKE %s
    AND b."Code" LIKE %s
    ORDER BY r."Code";''', (date_from, date_to, place_type + '%', building + '%'))
    aux = dbClient.fetchall()
    dbClient.disconnect()
    list = [item for sub_list in aux for item in sub_list]
    return list

  except Exception as error:
    print(error)
    return None
