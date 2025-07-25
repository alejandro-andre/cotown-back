# ######################################################
# Imports
# ######################################################

# System includes
from datetime import datetime, timedelta
import logging
import json

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Cotown includes
from library.services.config import settings


# ######################################################
# Dashboard
# ######################################################

def q_labels(dbClient, id, locale):

  # Get labels
  con = dbClient.getconn()
  cur = dbClient.execute(con,
    '''
    SELECT "values", "labels"
    FROM "Models"."EnumType" et
    INNER JOIN "Models"."EnumTypeLabel" ON container = et.id
    WHERE et.id = %s AND locale = %s;
    ''',
    (id, locale,))
  result = cur.fetchone()
  cur.close()
  dbClient.putconn(con)
  return json.dumps(result, default=str)


# ######################################################
# Dashboard operaciones
# ######################################################

def sql_dashboard_operaciones(status, vars):

  # Params
  date_from       = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d') if not vars.get('date_from') else vars.get('date_from')
  date_checkinto  = (datetime.now() + timedelta(days=settings.CHECKINDAYS)).strftime('%Y-%m-%d') if not vars.get('date_to') else vars.get('date_to')
  date_checkoutto = (datetime.now() + timedelta(days=settings.CHECKOUTDAYS)).strftime('%Y-%m-%d') if not vars.get('date_to') else vars.get('date_to')
  building        = vars.get('building')
  buildings       = vars.getlist('building[]')
  location        = vars.get('location')

  # Get bookings
  select = '''
    SELECT 
      b.id, 
      b."Status", 
      b."Date_from", 
      b."Date_to", 
      b."Check_in",
      b."Check_out",
      b."Confirmation_date",
      COALESCE(b."Check_in", b."Date_from") AS "Date_in",
      COALESCE(b."Check_out", b."Date_to") AS "Date_out",
      b."New_check_out",
      b."Old_check_out",
      b."Check_in_time",
      b."Arrival", 
      b."Flight", 
      b."Check_in_room_ok",
      b."Check_in_notice_ok",
      b."Check_in_keys_ok",
      b."Check_in_keyless_ok", 
      b."Check_out_keys_ok",
      b."Check_out_keyless_ok", 
      b."Check_out_revision_ok", 
      b."Issues", 
      b."Issues_ok", 
      b."Damages", 
      b."Damages_ok", 
      b."Comments",
      b."Origin_id",
      b."Destination_id",
      b."Eco_ext_change_ok",
      b."Eco_ext_keyless_ok",
      b."Cha_ext",
      ct."Name" AS "Option_in",
      cto."Name" AS "Option_out",
      CASE WHEN b2."Name" IS NULL THEN b1."Name" ELSE b2."Name" END as "Building",
      r."Code" as "Resource",
      c."Name",
      c."Email",
      c."Phones",
      p.id AS "Payment_id",
      p."Payment_date"      
    FROM "Booking"."Booking" b
      INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
      INNER JOIN "Building"."Building" b1 ON b1.id = b."Building_id"
      LEFT JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
      LEFT JOIN "Building"."Building" b2 ON b2.id = r."Building_id"
      LEFT JOIN "Geo"."District" d ON d.id = b1."District_id"
      LEFT JOIN "Billing"."Payment" p ON p."Booking_id" = b.id AND p."Payment_type" = 'checkin' AND p."Amount" > 0
      LEFT JOIN "Booking"."Checkin_type" ct ON ct.id = b."Check_in_option_id"
      LEFT JOIN "Booking"."Checkin_type" cto ON cto.id = b."Check_out_option_id" '''

  # All confirmed
  if status == 'ok':
    sql = select + '''
    WHERE b."Status" IN (\'firmacontrato\', \'contrato\', \'checkinconfirmado\') '''

  # Check-ins
  elif status == 'checkin':
    sql = select + '''
    WHERE (b."Status" =\'checkin\' OR (COALESCE(b."Check_in", b."Date_from") <= CURRENT_DATE AND b."Status" IN (\'firmacontrato\', \'contrato\', \'checkinconfirmado\'))) '''

  # Next check-ins
  elif status in ('next', 'nextin'):
    sql = select + f'''
    WHERE b."Status" IN (\'firmacontrato\', \'contrato\', \'checkinconfirmado\')
      AND COALESCE(b."Check_in", b."Date_from") BETWEEN '{date_from}' AND '{date_checkinto}' '''

  # Next check-outs
  elif status == 'nextout':
    sql = select + f'''
    WHERE b."Status" IN (\'inhouse\')
      AND COALESCE(b."Check_out", b."Date_to") BETWEEN '{date_from}' AND '{date_checkoutto}' '''

  # Check-ins with issues
  elif status == 'issues':
    sql = select + f'''
    WHERE b."Status" IN (\'inhouse\')
      AND b."Issues" IS NOT NULL
      AND b."Issues_ok" <> TRUE
      AND COALESCE(b."Check_in", b."Date_from") BETWEEN '{date_from}' AND '{date_checkinto}' '''

  # ECO/EXT
  elif status == 'ecoext':
    sql = select + f'''
    WHERE b."Status" IN (\'inhouse\')
      AND COALESCE(b."New_check_out", COALESCE(b."Check_out", b."Date_to")) <> COALESCE(b."Check_out", b."Date_to")
      AND NOT b."Eco_ext_change_ok" '''

  # Other status
  else:
    sql = select + f'''
    WHERE b."Status" = '{status}' '''

  # Result
  if buildings:
    sql += f'''AND b2.id IN ({','.join(buildings)}) '''
  elif building:
    sql += f'''AND b2.id={building} '''
  if location:
    sql += f'''AND d."Location_id"={location} '''

  # SQL
  return sql


def q_dashboard_operaciones(dbClient, status=None, vars=None):

  # Connect
  con = dbClient.getconn()

  # Counters
  if status is None:
    result = {}  

    # Count by status
    cur = dbClient.execute(con, 'SELECT "Status", COUNT (*) FROM "Booking"."Booking" GROUP BY 1')
    for row in cur.fetchall():
      result[row[0]] = row[1]
    cur.close()

    # Count all confirmed
    cur = dbClient.execute(con, 'SELECT COUNT (*) FROM "Booking"."Booking" WHERE "Status" IN (\'firmacontrato\', \'contrato\', \'checkinconfirmado\')')
    row = cur.fetchone()
    cur.close()
    result['ok'] = row[0]

    # Count nearest checkins
    cur = dbClient.execute(con, 'SELECT COUNT (*) FROM "Booking"."Booking" WHERE "Status" IN (\'firmacontrato\', \'contrato\', \'checkinconfirmado\') AND COALESCE("Check_in", "Date_from") BETWEEN CURRENT_DATE + INTERVAL \'1 days\' AND CURRENT_DATE + INTERVAL \'' + str(settings.CHECKINDAYS) + ' days\'')
    row = cur.fetchone()
    cur.close()
    result['next'] = row[0]

    # Count nearest checkouts
    cur = dbClient.execute(con, 'SELECT COUNT (*) FROM "Booking"."Booking" WHERE "Status" IN (\'inhouse\') AND COALESCE("Check_out", "Date_to") BETWEEN CURRENT_DATE + INTERVAL \'1 days\' AND CURRENT_DATE + INTERVAL \'' + str(settings.CHECKOUTDAYS) + ' days\'')
    row = cur.fetchone()
    cur.close()
    result['nextout'] = row[0]

    # Return
    return result

  # Get bookings
  cur = dbClient.execute(con, sql_dashboard_operaciones(status, vars), vars)
  result = json.dumps([dict(row) for row in cur.fetchall()], default=str)
  cur.close()
  dbClient.putconn(con)
  return result


# ######################################################
# Dashboard LAU
# ######################################################

def sql_dashboard_lau(status, vars):

  # Params
  date_from  = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d') if not vars.get('date_from') else vars.get('date_from')
  date_to    = (datetime.now() + timedelta(days=settings.LAUDAYS)).strftime('%Y-%m-%d') if not vars.get('date_to') else vars.get('date_to')
  building   = vars.get('building')
  buildings  = vars.getlist('building[]')
  location   = vars.get('location')

  # Get bookings
  select = '''
    SELECT 
      b.id, 
      b."Date_from", b."Date_to", b."Date_estimated",
      b."Deposit", b."Deposit_required", b."Deposit_return_date",
      b."Compensation", b."Compensation_date",
      b."ITP_required_date", b."ITP_date", 
      b."Burofax_date",
      r."Code" AS "Resource", 
      bu."Name" AS "Building",
      c."Name", c."Email", c."Phones"
    FROM "Booking"."Booking_other" b
      INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
      INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
      INNER JOIN "Building"."Building" bu ON bu.id = r."Building_id"
      LEFT JOIN "Geo"."District" d ON d.id = bu."District_id"
  '''

  # Devolutions
  if status == 'dev':
    sql = select + f'''
    WHERE b."Deposit_required_date" BETWEEN '{date_from}' AND '{date_to}' '''   

  # ITP
  elif status == 'itp':
    sql = select + f'''
    WHERE b."ITP_required_date" BETWEEN '{date_from}' AND '{date_to}' '''   

  # End of contract
  elif status == 'end':
    sql = select + f'''
    WHERE b."Date_to" BETWEEN '{date_from}' AND '{date_to}' '''   

  # Result
  if buildings:
    sql += f'''AND bu.id IN ({','.join(buildings)}) '''
  elif building:
    sql += f'''AND bu.id={building} '''
  if location:
    sql += f'''AND d."Location_id"={location} '''

  # SQL
  return sql


def q_dashboard_lau(dbClient, status=None, vars=None):

  # Connect
  con = dbClient.getconn()
 
  # Get bookings
  cur = dbClient.execute(con, sql_dashboard_lau(status, vars), vars)
  result = json.dumps([dict(row) for row in cur.fetchall()], default=str)
  cur.close()
  dbClient.putconn(con)
  return result


# ######################################################
# Dashboard Administration
# ######################################################

def sql_dashboard_payments(vars):

  # Params
  date_from  = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d') if not vars.get('date_from') else vars.get('date_from')
  date_to    = (datetime.now() + timedelta(days=settings.LAUDAYS)).strftime('%Y-%m-%d') if not vars.get('date_to') else vars.get('date_to')
  building   = vars.get('building')
  buildings  = vars.getlist('building[]')
  location   = vars.get('location')

  # Additional where
  where = ''
  if buildings:
    where += f'''AND bu.id IN ({','.join(buildings)}) '''
  elif building:
    where += f'''AND bu.id={building} '''
  if location:
    where += f'''AND d."Location_id"={location} '''

  # Pending payments
  sql = f'''
    SELECT
      p.id,
      p."Issued_date",
      p."Concept", 
      p."Payment_auth", 
      p."Payment_date", 
      p."Amount",
      p."Comments",
      pm."Name" AS "Payment_method",
      c."Name" AS "Customer",
      c."Email" AS "Email",
      b.id AS "Booking_id", 
      b."Date_from", b."Date_to",
      r."Code" AS "Resource",
      bu."Code" AS "Building",
      STRING_AGG(i."Code", ', ') AS "Invoices",
      SUM(i."Total") AS "Invoice_total",
      p."Warning_1", p."Warning_2", p."Warning_3"
    FROM "Billing"."Payment" p
      INNER JOIN "Billing"."Payment_method" pm ON pm.id = p."Payment_method_id"
      INNER JOIN "Billing"."Invoice" i ON i."Payment_id" = p.id
      INNER JOIN "Booking"."Booking" b ON b.id = p."Booking_id"
      INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
      INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
      INNER JOIN "Building"."Building" bu ON bu.id = r."Building_id"
      LEFT JOIN "Geo"."District" d ON d.id = bu."District_id"
    WHERE p."Issued_date" BETWEEN '{date_from}' AND '{date_to}'
      AND p."Amount" > 0 
      AND (p."Payment_date" IS NULL OR p."Payment_auth" IS NULL)
      AND pm."Name" NOT LIKE '%%garantía%%'
      AND pm."Name" NOT LIKE '%%Rectificativa%%'
      {where}
    GROUP BY
      p.id,
      p."Issued_date",
      p."Concept", 
      p."Payment_auth", 
      p."Payment_date", 
      p."Amount",
      p."Comments",
      c."Name",
      c."Email",
      pm."Name",
      b.id, 
      b."Date_from", b."Date_to",
      r."Code",
      bu."Code"
    '''

  # SQL
  return sql


def sql_dashboard_deposits(vars):

  # Params
  date_from  = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d') if not vars.get('date_from') else vars.get('date_from')
  date_to    = (datetime.now() + timedelta(days=settings.LAUDAYS)).strftime('%Y-%m-%d') if not vars.get('date_to') else vars.get('date_to')
  building   = vars.get('building')
  buildings  = vars.getlist('building[]')
  location   = vars.get('location')

  # Additional where
  where = ''
  if buildings:
    where += f'''AND bu.id IN ({','.join(buildings)}) '''
  elif building:
    where += f'''AND bu.id={building} '''
  if location:
    where += f'''AND d."Location_id"={location} '''

  # Deposits
  sql = f'''
    SELECT 
      b.id AS "Booking_id",
      b."Date_from", b."Date_to",
      b."Deposit_required", b."Date_deposit_required", b."Deposit_returned", b."Date_deposit_returned", 
      CASE 
        WHEN b."Deposit_locked" THEN 1
        ELSE 0
      END AS "Deposit_locked",
      c."Name" AS "Customer",
      c."Email" AS "Email",
      r."Code" AS "Resource",
      bu."Code" AS "Building"
    FROM "Booking"."Booking" b 
      INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
      INNER JOIN "Customer"."Customer" c ON c.id = b."Customer_id"
      INNER JOIN "Building"."Building" bu ON bu.id = r."Building_id"
      LEFT JOIN "Geo"."District" d ON d.id = bu."District_id"
    WHERE b."Status" = 'devolvergarantia' 
      AND (b."Date_deposit_required" BETWEEN '{date_from}' AND '{date_to}' OR b."Date_deposit_required" IS NULL)
      {where}
    ORDER BY 1
  '''   

  # SQL
  return sql


def q_dashboard_payments(dbClient, vars=None):

  # Connect
  con = dbClient.getconn()
 
  # Get bookings
  cur = dbClient.execute(con, sql_dashboard_payments(vars), vars)
  result = json.dumps([dict(row) for row in cur.fetchall()], default=str)
  cur.close()
  dbClient.putconn(con)
  return result


def q_dashboard_deposits(dbClient, vars=None):

  # Connect
  con = dbClient.getconn()
 
  # Get bookings
  cur = dbClient.execute(con, sql_dashboard_deposits(vars), vars)
  result = json.dumps([dict(row) for row in cur.fetchall()], default=str)
  cur.close()
  dbClient.putconn(con)
  return result


# ######################################################
# Web - Flat prices
# ######################################################

def q_flat_prices(dbClient, segment, year):

  # Connect
  con = dbClient.getconn()

  # Get prices
  sql = '''
    SELECT
      r."Building_id", rft.id AS "Flat_type_id", rfst.id AS "Flat_subtype_id", rfst."Code" AS "Flat_subtype",
      MIN(ROUND(pd."Services" + pr."Multiplier" * pd."Rent_long", 0)) AS "Rent_long",
      MIN(ROUND(pd."Services" + pr."Multiplier" * pd."Rent_medium", 0)) AS "Rent_medium",
      MIN(ROUND(pd."Services" + pr."Multiplier" * pd."Rent_short", 0)) AS "Rent_short",
      MIN(ROUND(px."Services" + pr."Multiplier" * px."Rent_long", 0)) AS "Rent_long_next",
      MIN(ROUND(px."Services" + pr."Multiplier" * px."Rent_medium", 0)) AS "Rent_medium_next",
      MIN(ROUND(px."Services" + pr."Multiplier" * px."Rent_short", 0)) AS "Rent_short_next",
      COUNT(*) AS "Qty"
    FROM
      "Resource"."Resource" r
      INNER JOIN "Building"."Building" b ON r."Building_id" = b.id
      INNER JOIN "Resource"."Resource_flat_type" rft ON r."Flat_type_id" = rft.id
      INNER JOIN "Resource"."Resource_flat_subtype" rfst ON r."Flat_subtype_id" = rfst.id
      INNER JOIN "Billing"."Pricing_rate" pr ON r."Rate_id"  = pr.id
      INNER JOIN "Billing"."Pricing_detail" pd ON pd."Building_id" = r."Building_id" AND pd."Flat_type_id" = r."Flat_type_id" AND pd."Place_type_id" IS NULL
      INNER JOIN "Billing"."Pricing_detail" px ON px."Building_id" = r."Building_id" AND px."Flat_type_id" = r."Flat_type_id" AND px."Place_type_id" IS NULL
    WHERE r."Sale_type" IN ('ambos', 'completo')
      AND pd."Year" = %s
      AND px."Year" = %s
      AND b."Segment_id" = %s
    GROUP BY 1, 2, 3, 4
    ORDER BY 1, 2, 3;
  '''
  cur = dbClient.execute(con, sql, (year, year + 1, segment))

  # Obtener los resultados de la consulta
  results = cur.fetchall()

  # Crear una estructura de datos para almacenar los resultados agrupados
  grouped_data = []

  # Procesar los resultados y agruparlos en dos niveles (Building, Flat_type)
  for row in results:
     
    # Building
    building_index = next((index for (index, d) in enumerate(grouped_data) if d['id'] == row['Building_id']), None)
    if building_index is None:
      grouped_data.append({
        'id': row['Building_id'],
        'Flat_subtypes': []
      })
      building_index = len(grouped_data) - 1

    # Place type
    flat_type_index = next((index for (index, d) in enumerate(grouped_data[building_index]['Flat_subtypes']) if d['Code'] == row['Flat_subtype']), None)
    if flat_type_index is None:
      grouped_data[building_index]['Flat_subtypes'].append({
        'id': row['Flat_subtype_id'],
        'Flat_type_id': row['Flat_type_id'],
        'Code': row['Flat_subtype'],
        'Rent_long': int(row['Rent_long']),
        'Rent_medium': int(row['Rent_medium']),
        'Rent_short': int(row['Rent_short']),
        'Rent_long_next': int(row['Rent_long_next']),
        'Rent_medium_next': int(row['Rent_medium_next']),
        'Rent_short_next': int(row['Rent_short_next']),
        'Qty': row['Qty']
      })

  # To JSON
  result = json.dumps(grouped_data, default=str)
 
  # Disconnect
  cur.close()
  dbClient.putconn(con)

  # Return
  return result


# ######################################################
# Web - Price by place/flat types info
# ######################################################

def q_room_prices(dbClient, segment, year):

  # Connect
  con = dbClient.getconn()

  # Get prices
  sql = '''
    SELECT
      r."Building_id", rpt.id AS "Place_type_id", rft.id AS "Flat_type_id", 
      rpt."Code" AS "Place_type", rft."Code" AS "Flat_type",
      MIN(ROUND(pd."Services" + pr."Multiplier" * pd."Rent_long", 0)) AS "Rent_long",
      MIN(ROUND(pd."Services" + pr."Multiplier" * pd."Rent_medium", 0)) AS "Rent_medium",
      MIN(ROUND(pd."Services" + pr."Multiplier" * pd."Rent_short", 0)) AS "Rent_short",
      MIN(ROUND(px."Services" + pr."Multiplier" * px."Rent_long", 0)) AS "Rent_long_next",
      MIN(ROUND(px."Services" + pr."Multiplier" * px."Rent_medium", 0)) AS "Rent_medium_next",
      MIN(ROUND(px."Services" + pr."Multiplier" * px."Rent_short", 0)) AS "Rent_short_next",
      COUNT(*) AS "Qty"
    FROM
      "Resource"."Resource" r
      INNER JOIN "Building"."Building" b ON r."Building_id" = b.id
      INNER JOIN "Resource"."Resource_flat_type" rft ON r."Flat_type_id" = rft.id
      INNER JOIN "Resource"."Resource_place_type" rpt ON r."Place_type_id" = rpt.id
      INNER JOIN "Billing"."Pricing_rate" pr ON r."Rate_id"  = pr.id
      INNER JOIN "Billing"."Pricing_detail" pd ON pd."Building_id" = r."Building_id" AND pd."Flat_type_id" = r."Flat_type_id" AND pd."Place_type_id" = r."Place_type_id"
      INNER JOIN "Billing"."Pricing_detail" px ON px."Building_id" = r."Building_id" AND px."Flat_type_id" = r."Flat_type_id" AND px."Place_type_id" = r."Place_type_id"
    WHERE r."Sale_type" in ('ambos', 'plazas')
      AND pd."Year" = %s
      AND px."Year" = %s
      AND b."Segment_id" = %s
      AND rpt."Code" NOT LIKE 'DUI%%'
    GROUP BY 1, 2, 3, 4, 5
    ORDER BY 1, 2, 3
  '''
  cur = dbClient.execute(con, sql, (year, year + 1, segment))

  # Obtener los resultados de la consulta
  results = cur.fetchall()
  cur.close()

  # Crear una estructura de datos para almacenar los resultados agrupados
  grouped_data = []

  # Procesar los resultados y agruparlos en tres niveles (Building, Place_type, Flat_type)
  for row in results:
     
    # Building
    building_index = next((index for (index, d) in enumerate(grouped_data) if d['id'] == row['Building_id']), None)
    if building_index is None:
      grouped_data.append({
        'id': row['Building_id'],
        'Place_types': []
      })
      building_index = len(grouped_data) - 1

    # Place type
    place_type_index = next((index for (index, d) in enumerate(grouped_data[building_index]['Place_types']) if d['Code'] == row['Place_type']), None)
    if place_type_index is None:
      grouped_data[building_index]['Place_types'].append({
        'id': row['Place_type_id'],
        'Code': row['Place_type'],
        'Flat_types': []
      })
      place_type_index = len(grouped_data[building_index]['Place_types']) - 1

    # Flat type
    grouped_data[building_index]['Place_types'][place_type_index]['Flat_types'].append({
      'id': row['Flat_type_id'],
      'Code': row['Flat_type'],
      'Rent_long': int(row['Rent_long']),
      'Rent_medium': int(row['Rent_medium']),
      'Rent_short': int(row['Rent_short']),
      'Rent_long_next': int(row['Rent_long_next']),
      'Rent_medium_next': int(row['Rent_medium_next']),
      'Rent_short_next': int(row['Rent_short_next']),
      'Qty': row['Qty']
    })

  # To JSON
  result = json.dumps(grouped_data, default=str)
 
  # Disconnect
  dbClient.putconn(con)

  # Return
  return result


# ######################################################
# Web - Amenities
# ######################################################

def q_room_amenities(dbClient, segment):

  # Connect
  con = dbClient.getconn()

  # Get amenities
  sql = '''
  SELECT
    b.id, rpt."Code" AS "Place_type", rft."Code" AS "Flat_type", rat."Name", rat."Name_en", rat."Increment"::INTEGER, COUNT(*) AS "Qty"
  FROM
    "Resource"."Resource_amenity" ra
    INNER JOIN "Resource"."Resource_amenity_type" rat ON rat.id = ra."Amenity_type_id"
    INNER JOIN "Resource"."Resource" r ON r.id = ra."Resource_id"
    INNER JOIN "Resource"."Resource_flat_type" rft ON r."Flat_type_id" = rft.id
    INNER JOIN "Resource"."Resource_place_type" rpt ON r."Place_type_id" = rpt.id
    INNER JOIN "Building"."Building" b ON r."Building_id" = b.id
  WHERE b."Segment_id" = %s
  GROUP BY 1, 2, 3, 4, 5, 6
  ORDER BY 1, 2, 3, 4
  '''
  cur = dbClient.execute(con, sql, (segment, ))

  # To JSON
  result = json.dumps([dict(row) for row in cur.fetchall()], default=str)
 
  # Disconnect
  cur.close()
  dbClient.putconn(con)

  # Return
  return result


# ######################################################
# Get payment
# ######################################################

def q_get_payment(dbClient, id, generate_order=False):

  try:
    # Get payment
    con = dbClient.getconn()
    cur = dbClient.execute(con, '''
      SELECT p.id, p."Issued_date", p."Concept", p."Amount", p."Payment_order", p."Pos"  
      FROM "Billing"."Payment" p
      INNER JOIN "Customer"."Customer" c ON c.id = p."Customer_id"
      WHERE p.id = %s
      AND c."Id_type_id" IS NOT NULL 
      AND c."Document" IS NOT NULL
      AND c."Address" IS NOT NULL
      AND c."Zip" IS NOT NULL
      AND c."City" IS NOT NULL
      AND c."Country_id" IS NOT NULL
    ''', (id,))
    result = cur.fetchone()
    cur.close()
    if result is None:
      dbClient.putconn(con)
      return None
   
    # Get data
    aux = dict(result)
    aux['Issued_date'] = aux['Issued_date'].strftime("%Y-%m-%d")
    if aux['Pos'] is None:
      aux['Pos'] = 'delegado'

    if generate_order:

      # Get next order num
      cur = dbClient.execute(con, 'SELECT nextval(\'"Auxiliar"."Sequence_Payment_order_seq"\')')
      val = cur.fetchone()
      cur.close()
      order = "{:02d}{:05d}{:05d}".format(datetime.now().year - 2000, id, val[0])
      aux['Payment_order'] = order

      # Update payment
      dbClient.execute(con, 'UPDATE "Billing"."Payment" SET "Payment_order"=%s WHERE id=%s', (order, id))
      con.commit()

    # Prepare response
    dbClient.putconn(con)
    logger.debug(aux)
    return aux

  except Exception as error:
    logger.error(error)
    con.rollback()
    return None


# ######################################################
# Update payment
# ######################################################

def q_put_payment(dbClient, id, auth, date):

  try:
    con = dbClient.getconn()
    dbClient.execute(con, 'UPDATE "Billing"."Payment" SET "Payment_auth" = %s, "Payment_date" = %s WHERE id=%s', (auth, date, id))
    con.commit()
    dbClient.putconn(con)
    return True

  except Exception as error:
    logger.error(error)
    con.rollback()
    return False


# ######################################################
# Get provider
# ######################################################

def get_provider(dbClient, id):

  try:
    con = dbClient.getconn()
    cur = dbClient.execute(con, 'SELECT id, "Name", "Email", "Document", "User_name" FROM "Provider"."Provider" WHERE id=%s', (id,))
    aux = cur.fetchone()
    dbClient.putconn(con)
    logger.debug(aux)
    return aux

  except Exception as error:
    logger.error(error)
    con.rollback()
    return None

# ######################################################
# Get customer
# ######################################################

def get_customer(dbClient, id):

  try:
    con = dbClient.getconn()
    cur = dbClient.execute(con, 'SELECT id, "Name",  "Email", "Document", "User_name" FROM "Customer"."Customer" WHERE id=%s', (id,))
    aux = cur.fetchone()
    dbClient.putconn(con)
    logger.debug(aux)
    return aux

  except Exception as error:
    logger.error(error)
    con.rollback()
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
    con = dbClient.getconn()

    # Create user
    dbClient.execute(con, 'CREATE ROLE ' + username + ' PASSWORD %s NOSUPERUSER''', (password,))
    cur = dbClient.execute(con, 'INSERT INTO "Models"."User" ("username", "email", "password") VALUES (%s, %s, %s) RETURNING id', (username, email, password) )
    userid = cur.fetchone()[0]
    cur.close()

    # Create role provider
    if role == 200:
      dbClient.execute(con, 'GRANT "provider" TO ' + username)
      dbClient.execute(con, 'INSERT INTO "Models"."UserRole" ("user", "role") VALUES (%s, %s)', (userid, role))
      dbClient.execute(con, 'UPDATE "Provider"."Provider" SET "User_name" = %s WHERE id = %s', (username, id))

    # Create role customer
    if role == 300:
      dbClient.execute(con, 'GRANT "customer" TO ' + username)
      dbClient.execute(con, 'INSERT INTO "Models"."UserRole" ("user", "role") VALUES (%s, %s)', (userid, role))
      dbClient.execute(con, 'UPDATE "Customer"."Customer" SET "User_name" = %s WHERE id = %s', (username, id))
      dbClient.execute(con, 'INSERT INTO "Customer"."Customer_email" ("Customer_id", "Template", "Entity_id") VALUES (%s, %s, %s)', (id, 'bienvenida', id))
   
    # Commit
    con.commit()
    dbClient.putconn(con)
    return userid

  except Exception as error:
    logger.error(error)
    con.rollback()
    return None


# ######################################################
# Delete airflows user
# ######################################################

def delete_airflows_user(dbClient, id):

  try:
    # Connect
    con = dbClient.getconn()
    dbClient.execute(con, 'DELETE FROM "Models"."User" WHERE id = %s', (id,) )
    con.commit()
    dbClient.putconn(con)
    return id

  except Exception as error:
    logger.error(error)
    con.rollback()
    return None
 

# ######################################################
# Booking status
# ######################################################

def q_booking_status(dbClient, id, status):

  try:
    con = dbClient.getconn()
    dbClient.execute(con, 'UPDATE "Booking"."Booking" SET "Status" = %s WHERE id = %s', (status, id))
    con.commit()
    dbClient.putconn(con)
    return True

  except Exception as error:
    logger.error(error)
    con.rollback()
    return False


# ######################################################
# Availability
# ######################################################

# Get ids of available resources of required typology between dates
def q_available_resources(dbClient, date_from, date_to, building, flat_type, place_type):

  if building is None:
    building = 0

  if place_type is None:
    place_type = 0
   
  if flat_type is None:
    flat_type = 0

  try:
    con = dbClient.getconn()
    cur = dbClient.execute(con, '''
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
    ORDER BY 1;
    ''', (date_to, date_from, building, building, flat_type, flat_type,place_type, place_type))
    aux = cur.fetchall()
    cur.close()
    dbClient.putconn(con)
    list = [item for sub_list in aux for item in sub_list]
    return list

  except Exception as error:
    logger.error(error)
    con.rollback()
    return None
  
# ######################################################
# Questionnaire
# ######################################################

# Upsert questionnaire answers
def q_questionnaire(dbClient, id, values, issues=None):

  try:
    con = dbClient.getconn()

    # Insert answers
    cur = dbClient.executemany(con, '''
    INSERT INTO "Booking"."Booking_answer" 
    ("Questionnaire_id", "Question_id", "Answer")
    VALUES (%s, %s, %s)
    ON CONFLICT ("Questionnaire_id", "Question_id")
    DO UPDATE SET "Answer" = EXCLUDED."Answer";
    ''', values)
    cur.close()

    # Update answer date
    cur = dbClient.execute(con, '''
    UPDATE "Booking"."Booking_questionnaire" 
    SET "Completed" = NOW()
    WHERE id = %s;
    ''', (id,))
    cur.close()
    
    # Update issues
    if issues is not None:
      cur = dbClient.execute(con, '''
      UPDATE "Booking"."Booking"
      SET "Issues" = %s
      FROM "Booking"."Booking_questionnaire" bq
      WHERE "Booking"."Booking".id = bq."Booking_id" AND bq.id = %s;
      ''', (issues, id,))
      cur.close()
    
    dbClient.putconn(con)
    return 'ok'

  except Exception as error:
    logger.error(error)
    con.rollback()
    return 'ko'


# ######################################################
# Next & Prev bookings
# ######################################################

def q_prev_next(dbClient):

  try:
    con = dbClient.getconn()
    cur = dbClient.execute(con, '''
      SELECT DISTINCT ON (b.id) b.id, COALESCE(b."Check_in", b."Date_from") AS "Date_in", prv.id AS "Prev_id", COALESCE(prv."Check_out", prv."Date_to") AS "Prev_date"
      FROM "Booking"."Booking" b
        INNER JOIN "Booking"."Booking" prv ON b."Resource_id" = prv."Resource_id" AND b.id != prv.id AND b."Customer_id" <> prv."Customer_id"
          AND prv."Date_to" BETWEEN b."Date_from" - INTERVAL '20 days' AND b."Date_from"
      WHERE b."Status" IN ('firmacontrato', 'contrato', 'checkinconfirmado')
      ORDER BY b.id, prv."Date_to" DESC;
    ''')
    prv = [dict(row) for row in cur.fetchall()]
    cur.close()
    cur = dbClient.execute(con, '''
      SELECT DISTINCT ON (b.id) b.id, nxt.id AS "Next_id", COALESCE(b."Check_out", b."Date_to") AS "Date_out", COALESCE(nxt."Check_in", nxt."Date_from") AS "Next_date"
      FROM "Booking"."Booking" b
        INNER JOIN "Booking"."Booking" nxt ON b."Resource_id" = nxt."Resource_id" AND b.id != nxt.id AND b."Customer_id" <> nxt."Customer_id"
          AND nxt."Date_from" BETWEEN b."Date_to" AND b."Date_to" + INTERVAL '20 days' 
      WHERE b."Status" IN ('inhouse')
      ORDER BY b.id, nxt."Date_from" ASC;
    ''')
    nxt = [dict(row) for row in cur.fetchall()]
    cur.close()
    dbClient.putconn(con)
    return json.dumps([prv, nxt], default=str)    
  
  except Exception as error:
    logger.error(error)
    con.rollback()
    return None


# ######################################################
# Change contract
# ######################################################

def q_change_contract(dbClient, id, dt, status):

  try:
    con = dbClient.getconn()
    dbClient.execute(con, 'UPDATE "Booking"."Booking" SET "Contract_signed" = %s, "Contract_status" = %s WHERE "Contract_id"=%s', (dt, status, id))
    con.commit()
    dbClient.putconn(con)
    return True

  except Exception as error:
    logger.error(error)
    con.rollback()
    return False