# ######################################################
# Imports
# ######################################################

# System includes
import logging
import datetime

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ######################################################
# Get payment
# ######################################################

def get_payment(dbClient, id, generate_order=False):

  try:
    # Get payment
    dbClient.connect()
    dbClient.select('SELECT id, "Issued_date", "Concept", "Amount", "Payment_order" FROM "Billing"."Payment" WHERE id=%s', (id,))
    result = dbClient.fetch()
    if result is None:
      dbClient.disconnect()
      return None
    
    # Get data
    aux = dict(result)
    aux['Issued_date'] = aux['Issued_date'].strftime("%Y-%m-%d")

    if generate_order:

      # Get next order num
      dbClient.select('SELECT nextval(\'"Auxiliar"."Sequence_Payment_order_seq"\')')
      val = dbClient.fetch()
      order = "{:02d}{:05d}{:05d}".format(datetime.datetime.now().year - 2000, id, val[0])
      aux['Payment_order'] = order

      # Update payment
      dbClient.execute('UPDATE "Billing"."Payment" SET "Payment_order"=%s WHERE id=%s', (order, id))
      dbClient.commit()

    # Prepare response
    dbClient.disconnect()
    logger.debug(aux)
    return aux

  except Exception as error:
    logger.error(error)
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
    logger.error(error)
    return False


# ######################################################
# Get provider
# ######################################################

def get_provider(dbClient, id):

  try:
    dbClient.connect()
    dbClient.select('SELECT id, "Name", "Email", "Document", "User_name" FROM "Provider"."Provider" WHERE id=%s', (id,))
    aux = dbClient.fetch()
    dbClient.disconnect()
    logger.debug(aux)
    return aux

  except Exception as error:
    logger.error(error)
    return None

# ######################################################
# Create user
# ######################################################

def create_airflows_user(dbClient, user, role):

  # Provider fields
  id = user['id']
  email = user['Email']
  username = user['User_name'].lower()
  password = username + 'p4$$w0rd'

  try:
    # Connect
    dbClient.connect()

    # Create user
    dbClient.execute('CREATE ROLE ' + username + ' PASSWORD %s NOSUPERUSER''', (password,)) 
    dbClient.execute('INSERT INTO "Models"."User" ("username", "email", "password") VALUES (%s, %s, %s) RETURNING id', (username, email, password) )
    userid = dbClient.returning()[0]

    # Create role
    dbClient.execute('GRANT "user" TO ' + username)
    dbClient.execute('INSERT INTO "Models"."UserRole" ("user", "role") VALUES (%s, %s)', (userid, role))

    # Update table
    if role == 200:
      dbClient.execute('UPDATE "Provider"."Provider" SET "User_name" = %s WHERE id = %s', (username, id))

    # Update table and send mail
    if role == 300:
      dbClient.execute('UPDATE "Customer"."Customer" SET "User_name" = %s WHERE id = %s', (username, id))
      dbClient.execute('INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (%s, %s, %s)', (id, 'bienvenida', id))
    
    # Commit
    dbClient.commit()
    dbClient.disconnect()
    return userid

  except Exception as error:
    dbClient.rollback()
    logger.error(error)
    return None


# ######################################################
# Delete user
# ######################################################

def delete_airflows_user(dbClient, id):

  try:
    # Connect
    dbClient.connect()
    dbClient.execute('DELETE FROM "Models"."User" WHERE id = %s', (id,) )
    dbClient.commit()
    dbClient.disconnect()
    return id

  except Exception as error:
    dbClient.rollback()
    logger.error(error)
    return None
  
  
  # ######################################################
# Get customer
# ######################################################

def get_customer(dbClient, id):

  try:
    dbClient.connect()
    dbClient.select('SELECT id, "Name",  "Email", "Document", "User_name" FROM "Customer"."Customer" WHERE id=%s', (id,))
    aux = dbClient.fetch()
    dbClient.disconnect()
    logger.debug(aux)
    return aux

  except Exception as error:
    logger.error(error)
    return None


# ######################################################
# Availability
# ######################################################

def availability(dbClient, date_from, date_to, building, flat_type, place_type):

  if building is None:
    building = ''

  if place_type is None:
    place_type = ''
    
  if flat_type is None:
    flat_type = ''

  try:
    dbClient.connect()
    dbClient.select('''
    SELECT r."Code"
    FROM "Resource"."Resource" r
    INNER JOIN "Building"."Building" b ON b.id = r."Building_id" 
    INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id" 
    INNER JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id" 
    LEFT JOIN "Booking"."Booking_detail" bd ON bd."Resource_id" = r.id 
    AND bd."Date_from" <= %s 
    AND bd."Date_to" >= %s
    WHERE bd.id IS NULL 
    AND rft."Code" LIKE %s
    AND rpt."Code" LIKE %s
    AND b."Code" LIKE %s
    ORDER BY r."Code";''', (date_to, date_from, flat_type + '%', place_type + '%', building + '%'))
    aux = dbClient.fetchall()
    dbClient.disconnect()
    list = [item for sub_list in aux for item in sub_list]
    logger.debug(list)
    return list

  except Exception as error:
    logger.error(error)
    dbClient.rollback()
    return None
