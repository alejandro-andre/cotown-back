# ######################################################
# Imports
# ######################################################

# System includes
import logging
import datetime

# Logging
import logging
logger = logging.getLogger(__name__)


# ######################################################
# Get payment
# ######################################################

def get_payment(dbClient, id, generate_order=False):

  try:
    # Get payment
    dbClient.connect()
    dbClient.select('SELECT id, "Issued_date", "Concept", "Amount", "Payment_order" FROM "Billing"."Payment" WHERE id=%s', (id,))
    aux = dict(dbClient.fetch())
    aux['Issued_date'] = aux['Issued_date'].strftime("%Y-%m-%d")

    if generate_order:

      # Get next order num
      dbClient.select('SELECT nextval(\'"Auxiliar"."Secuence_Payment_order_seq"\')')
      val = dbClient.fetch()
      order = "{:02d}{:05d}{:05d}".format(datetime.datetime.now().year - 2000, id, val[0])
      aux['Payment_order'] = order

      # Update payment
      dbClient.execute('UPDATE "Billing"."Payment" SET "Payment_order"=%s WHERE id=%s', (order, id))
      dbClient.commit()

    # Prepare response
    dbClient.disconnect()
    logging.debug(aux)
    return aux

  except Exception as error:
    logging.error(error)
    return None


# ######################################################
# Update payment
# ######################################################

def put_payment(dbClient, id, auth, date):

  try:
    dbClient.connect()
    dbClient.execute('UPDATE "Billing"."Payment" SET "Payment_auth" = %s, "Payment_date" = %s WHERE id=%s', (auth, date, id))
    dbClient.commit()
    dbClient.disconnect()
    return True

  except Exception as error:
    logging.error(error)
    return False


# ######################################################
# Get provider
# ######################################################

def get_provider(dbClient, id):

  try:
    dbClient.connect()
    dbClient.select('SELECT id, "Name", "Last_name", "Email", "Document", "User_name" FROM "Provider"."Provider" WHERE id=%s', (id,))
    aux = dbClient.fetch()
    dbClient.disconnect()
    logging.debug(aux)
    return aux

  except Exception as error:
    logging.error(error)
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
    logging.debug(aux)
    return aux

  except Exception as error:
    logging.error(error)
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
    logging.error(error)
    return None
