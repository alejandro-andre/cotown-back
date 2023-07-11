# ######################################################
# Imports
# ######################################################

# System includes
import logging
import datetime
import json

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Cotown includes
from library.services.config import settings


# ######################################################
# Dashboard
# ######################################################

def labels(dbClient, id, locale):

  # Get labels
  dbClient.connect()
  dbClient.select('''
  SELECT "values", "labels" 
  FROM "Models"."EnumType" et 
  INNER JOIN "Models"."EnumTypeLabel" ON container = et.id 
  WHERE et.id = %s AND locale = %s;
  ''', (id, locale,))
  result = dbClient.fetch()
  dbClient.disconnect()
  return json.dumps(result, default=str)


# ######################################################
# Dashboard
# ######################################################

def dashboard(dbClient, status = None):

  # Connect
  dbClient.connect()

  # Counters
  if status is None:
    result = {}   

    # Count by status
    dbClient.select('SELECT "Status", COUNT (*) FROM "Booking"."Booking" GROUP BY 1')
    for row in dbClient.fetchall():
      result[row[0]] = row[1]

    # Count all confirmed
    dbClient.select('SELECT COUNT (*) FROM "Booking"."Booking" WHERE "Status" IN (\'firmacontrato\', \'contrato\', \'checkinconfirmado\')')
    row = dbClient.fetch()
    result['ok'] = row[0]

    # Count nearest checkins
    dbClient.select('SELECT COUNT (*) FROM "Booking"."Booking" WHERE GREATEST("Check_in", "Date_from") BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL \'' + str(settings.CHECKINDAYS) + ' days\'')
    row = dbClient.fetch()
    result['next'] = row[0]

  # Rows
  else:
    # Get bookings
    if status == 'ok':
      sql = '''
        SELECT b.id, b."Status", c."Name", b."Date_from", b."Date_to", b."Check_in", bu."Name" as "Building", r."Code" as "Resource"
        FROM "Booking"."Booking" b 
        INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id" 
        INNER JOIN "Building"."Building" bu ON bu.id = b."Building_id" 
        LEFT JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
        WHERE "Status" IN (\'firmacontrato\', \'contrato\', \'checkinconfirmado\')'''
      dbClient.select(sql)
    elif status == 'next':
      sql = '''
        SELECT b.id, b."Status", c."Name", b."Date_from", b."Date_to", b."Check_in", r."Code" as "Resource", b."Flight", b."Arrival", ct."Name" AS "Option"
        FROM "Booking"."Booking" b 
        INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id" 
        INNER JOIN "Building"."Building" bu ON bu.id = b."Building_id" 
        LEFT JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
        LEFT JOIN "Booking"."Checkin_type" ct ON ct.id = b."Check_in_option_id"
        WHERE GREATEST("Check_in", "Date_from") BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL \' ''' + str(settings.CHECKINDAYS) + ' days\''
      dbClient.select(sql)
    else:
      sql = '''
        SELECT b.id, b."Status", c."Name", b."Date_from", b."Date_to", b."Check_in", bu."Name" as "Building", r."Code" as "Resource"
        FROM "Booking"."Booking" b 
        INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id" 
        INNER JOIN "Building"."Building" bu ON bu.id = b."Building_id" 
        LEFT JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
        WHERE "Status" = %s'''
      dbClient.select(sql, (status,))

    # Result
    result = json.dumps([dict(row) for row in dbClient.fetchall()], default=str)

  # Disconnect
  dbClient.disconnect()

  # Return
  return result


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
# Create airflows user
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

    # Create role provider
    if role == 200:
      dbClient.execute('GRANT "provider" TO ' + username)
      dbClient.execute('INSERT INTO "Models"."UserRole" ("user", "role") VALUES (%s, %s)', (userid, role))
      dbClient.execute('UPDATE "Provider"."Provider" SET "User_name" = %s WHERE id = %s', (username, id))

    # Create role customer
    if role == 300:
      dbClient.execute('GRANT "customer" TO ' + username)
      dbClient.execute('INSERT INTO "Models"."UserRole" ("user", "role") VALUES (%s, %s)', (userid, role))
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
# Delete airflows user
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
# Booking status
# ######################################################

def booking_status(dbClient, id, status):

  try:
    dbClient.connect()
    dbClient.execute('UPDATE "Booking"."Booking" SET "Status" = %s WHERE id = %s', (status, id))
    dbClient.commit()
    dbClient.disconnect()
    return True

  except Exception as error:
    dbClient.rollback()
    logger.error(error)
    return False


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
    LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id" 
    LEFT JOIN "Booking"."Booking_detail" bd ON bd."Resource_id" = r.id 
    AND bd."Date_from" <= %s 
    AND bd."Date_to" >= %s
    WHERE bd.id IS NULL 
    AND (b.id = %s OR %s = 0)
    AND (rft.id = %s OR %s = 0)
    AND (rpt.id = %s OR %s = 0)
    ORDER BY r."Code";''', (date_to, date_from, building, building, flat_type, flat_type,place_type, place_type))
    aux = dbClient.fetchall()
    dbClient.disconnect()
    list = [item for sub_list in aux for item in sub_list]
    logger.debug(list)
    return list

  except Exception as error:
    logger.error(error)
    dbClient.rollback()
    return None
