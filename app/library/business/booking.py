# ######################################################
# Imports
# ######################################################

# System includes
from datetime import datetime
from dateutil import relativedelta

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ######################################################
# Misc functions
# ######################################################

def rent_info(date_from, date_to):

  # Calculate length type
  df = datetime.strptime(date_from, "%Y-%m-%d")
  dt = datetime.strptime(date_to, "%Y-%m-%d")
  difference = relativedelta.relativedelta(dt, df)
  months = difference.years * 12 + difference.months
  if months < 3:
    field = 'Rent_short'
  elif months < 7:
    field = 'Rent_medium'
  else:
    field = 'Rent_long'

  # Rates year
  year = df.year if df.month < 9 else df.year + 1
  return year, field


# ######################################################
# Booking queries
# ######################################################

# ------------------------------------------------------
# Generic query
# ------------------------------------------------------

def q(dbClient, sql, params):

  try:
    dbClient.connect()
    dbClient.select(sql, params)
    result = [dict(row) for row in dbClient.fetchall()]
    dbClient.disconnect()
    return result
 
  except Exception as error:
    logger.error(error)
    dbClient.rollback()
    return None


# ------------------------------------------------------
# Get genders
# ------------------------------------------------------

def q_genders(dbClient, lang):

  # Genders query
  l = '_en' if lang == 'en' else ''
  return q(dbClient, f'SELECT id, "Name{l}" AS "Name" FROM "Auxiliar"."Gender"', ())
 

# ------------------------------------------------------
# Get Reasons
# ------------------------------------------------------

def q_reasons(dbClient, lang):

  # Reasons query
  l = '_en' if lang == 'en' else ''
  return q(dbClient, f'SELECT id, "Name{l}" AS "Name" FROM "Booking"."Customer_reason"', ())
 

# ------------------------------------------------------
# Get Countries
# ------------------------------------------------------

def q_countries(dbClient, lang):

  # Countries query
  l = '_en' if lang == 'en' else ''
  return q(dbClient, f'SELECT id, "Name{l}" AS "Name", "Prefix" FROM "Geo"."Country"', ())
 

# ------------------------------------------------------
# Get information of existing typologies
# ------------------------------------------------------

def q_typologies(dbClient, segment):

  # SQL
  sql = '''
    SELECT l.id, l."Name",
      CASE
        WHEN b."Building_type_id" = 3 THEN 'rs'
        WHEN (r."Sale_type" = 'ambos' OR r."Sale_type" = 'plazas') THEN 'pc'
        WHEN (r."Sale_type" = 'ambos' OR r."Sale_type" = 'completo') THEN 'ap'
      END as "Sale_type",
      CASE
        WHEN rpt."Code" LIKE 'I\_%' THEN 'ind'
        WHEN rpt."Code" LIKE 'D\_%' THEN 'sha'
        ELSE 'apt'
      END as "Room_type",
      COUNT(*)
    FROM "Resource"."Resource" r
      INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
      INNER JOIN "Geo"."District" d on d.id = b."District_id"
      INNER JOIN "Geo"."Location" l on l.id = d."Location_id"
      LEFT JOIN "Resource"."Resource_place_type" rpt on rpt.id = r."Place_type_id"
    WHERE b."Building_type_id" < 4
      AND b."Active" 
      AND b."Segment_id" = {}
      AND "Sale_type" IS NOT NULL
      AND (rpt."Code" IS NULL OR rpt."Code" NOT LIKE 'DUI_%')
    GROUP BY 1, 2, 3, 4
    ORDER BY 1, 2, 3, 4
    '''.format(segment)

  try:

    # Read data
    dbClient.connect()
    dbClient.select(sql)
    data = dbClient.fetchall()
    dbClient.disconnect()

    # Prepare JSON
    output = []
    for item in data:
      rid = item['id']
      name = item['Name']
      sale_type = item['Sale_type']
      room_type = item['Room_type']
      count = item['count']
      city_entry = next((entry for entry in output if entry['id'] == rid), None)
      if not city_entry:
          city_entry = {'id': rid, 'Name': name, 'Sale_types': []}
          output.append(city_entry)
      sale_entry = next((entry for entry in city_entry['Sale_types'] if entry['Sale_type'] == sale_type), None)
      if not sale_entry:
          sale_entry = {'Sale_type': sale_type, 'Room_types': []}
          city_entry['Sale_types'].append(sale_entry)
      room_entry = {'Room_type': room_type, 'count': count}
      sale_entry['Room_types'].append(room_entry)
    return output

  except Exception as error:
    logger.error(error)
    dbClient.rollback()
    return None

# ------------------------------------------------------
# Search results
# ------------------------------------------------------

def q_book_search(dbClient, segment, lang, date_from, date_to, city, acom_type, room_type):
 
  # Query parameters
  l = '_en' if lang == 'en' else ''
  year, field = rent_info(date_from, date_to)
  place_type = 'I_%' if room_type == 'ind' else 'D\_%'
  building_type = (3,) if acom_type == 'rs' else (1, 2)

  # Rooms
  if acom_type == 'ap':
    sql = f'''
      SELECT
        b.id AS "Building_id", rfst.id AS "Place_type_id", rft.id AS "Flat_type_id",
        b."Code" AS "Building_code", rfst."Code" AS "Place_type_code", rft."Code" AS "Flat_type_code",
        b."Name" AS "Building_name", rfst."Name{l}" AS "Place_type_name", rft."Name{l}" AS "Flat_type_name",
        ROUND(pd."Services" + pr."Multiplier" * pd."{field}", 0) AS "Price", MIN(mrt.id) AS "Photo"
      FROM
        "Resource"."Resource" r
        INNER JOIN "Building"."Building" b ON r."Building_id" = b.id
        INNER JOIN "Geo"."District" d ON d.id = b."District_id"
        INNER JOIN "Billing"."Pricing_rate" pr ON r."Rate_id"  = pr.id
        INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
        INNER JOIN "Resource"."Resource_flat_subtype" rfst ON r."Flat_subtype_id" = rfst.id
        INNER JOIN "Billing"."Pricing_detail" pd ON pd."Building_id" = r."Building_id" AND pd."Flat_type_id" = r."Flat_type_id" AND pd."Place_type_id" IS NULL
        LEFT JOIN "Marketing"."Media_resource_type" mrt ON (mrt."Building_id" = b.id AND mrt."Flat_subtype_id" = rfst.id)
        LEFT JOIN "Booking"."Booking_detail" bd ON (bd."Resource_id" = r.id AND bd."Date_from" <= %s AND bd."Date_to" >= %s)
      WHERE bd.id IS NULL
        AND pd."Year" = %s
        AND b."Segment_id" = %s
        AND b."Building_type_id" < 3
        AND d."Location_id" = %s
      GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
      '''
    params = (date_to, date_from, year, segment, city, )
  else:
    sql = f'''
      SELECT
        b.id as "Building_id", rpt.id AS "Place_type_id", rft.id AS "Flat_type_id",
        b."Code" AS "Building_code", rpt."Code" AS "Place_type_code", rft."Code" AS "Flat_type_code",
        b."Name" as "Building_name", rpt."Name{l}" AS "Place_type_name", rft."Name{l}" AS "Flat_type_name",
        pd."Services" + ROUND(pr."Multiplier" * pd."{field}", 0) AS "Price", MIN(mrt.id) AS "Photo"
      FROM "Resource"."Resource" r
        INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
        INNER JOIN "Geo"."District" d ON d.id = b."District_id"
        INNER JOIN "Billing"."Pricing_rate" pr ON r."Rate_id"  = pr.id
        INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
        INNER JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
        INNER JOIN "Billing"."Pricing_detail" pd ON (pd."Building_id" = b.id AND pd."Flat_type_id" = rft.id AND pd."Place_type_id" = rpt.id)
        LEFT JOIN "Marketing"."Media_resource_type" mrt ON (mrt."Building_id" = b.id AND mrt."Place_type_id" = rpt.id)
        LEFT JOIN "Booking"."Booking_detail" bd ON (bd."Resource_id" = r.id AND bd."Date_from" <= %s AND bd."Date_to" >= %s)
      WHERE bd.id IS NULL
        AND pd."Year" = %s
        AND b."Segment_id" = %s
        AND b."Building_type_id" IN %s
        AND d."Location_id" = %s
        AND rpt."Code" LIKE %s
      GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
      '''
    params = (date_to, date_from, year, segment, building_type, city, place_type, )

  try:
    dbClient.connect()
    dbClient.select(sql, params)
    results = dbClient.fetchall()
    grouped_data = []
    for row in results:
       
      # Building/Place
      building_index = next((index for (index, d) in enumerate(grouped_data) if d['Building_id'] == row['Building_id'] and d['Place_type_code'] == row['Place_type_code']), None)
      if building_index is None:
        grouped_data.append({
          'Building_id': row['Building_id'],
          'Building_code': row['Building_code'],
          'Building_name': row['Building_name'],
          'Place_type_id': row['Place_type_id'],
          'Place_type_code': row['Place_type_code'],
          'Place_type_name': row['Place_type_name'],
          'Photo': row['Photo'],
          'Price': 99999,
          'Flat_types': []
        })
        building_index = len(grouped_data) - 1

      # Flat type
      price = int(row['Price'])
      if grouped_data[building_index]['Price'] > price:
        grouped_data[building_index]['Price'] = price
      grouped_data[building_index]['Flat_types'].append({
        'Flat_type_id': row['Flat_type_id'],
        'Flat_type_code': row['Flat_type_code'],
        'Flat_type_name': row['Flat_type_name'],
        'Price': price
      })

    dbClient.disconnect()
    return sorted(grouped_data, key=lambda x: x['Price'])
 
  except Exception as error:
    logger.error(error)
    dbClient.rollback()
    return None
 
# ------------------------------------------------------
# Get summary
# ------------------------------------------------------

def q_book_summary(dbClient, lang, date_from, date_to, building_id, place_type_id, flat_type_id, acom_type):

  # Query parameters
  l = '_en' if lang == 'en' else ''
  year, field = rent_info(date_from, date_to)

  # Private aparment
  if acom_type == 'ap':
    sql = f'''
      SELECT DISTINCT
        b."Name" as "Building_name", rfst."Name{l}" AS "Place_type_name", rft."Name{l}" AS "Flat_type_name",
        ROUND(pr."Multiplier" * COALESCE(pd."{field}", 0), 0) AS "Rent",
        COALESCE(pd."Services", 0) AS "Services", 
        COALESCE(pd."Limit", 0) as "Limit",
        COALESCE(pd."Deposit", 0) AS "Deposit", 
        COALESCE(pd."Booking_fee", 0) AS "Booking_fee",
        COALESCE(pd."Second_resident", 0) AS "Second_resident",
        COALESCE(pd."Final_cleaning", 0) AS "Final_cleaning"
      FROM "Resource"."Resource" r
        INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
        INNER JOIN "Billing"."Pricing_rate" pr ON r."Rate_id"  = pr.id
        INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
        INNER JOIN "Resource"."Resource_flat_subtype" rfst ON rfst.id = r."Flat_subtype_id"
        INNER JOIN "Billing"."Pricing_detail" pd ON (pd."Building_id" = b.id AND pd."Flat_type_id" = rft.id)
      WHERE pd."Year" = %s
        AND b.id = %s
        AND rfst.id = %s
        AND rft.id = %s
      LIMIT 1
      '''
  else:
    sql = f'''
      SELECT DISTINCT
        b."Name" as "Building_name", rpt."Name{l}" AS "Place_type_name", rft."Name{l}" AS "Flat_type_name",
        ROUND(pr."Multiplier" * COALESCE(pd."{field}", 0), 0) AS "Rent",
        COALESCE(pd."Services", 0) AS "Services", 
        COALESCE(pd."Limit", 0) as "Limit",
        COALESCE(pd."Deposit", 0) AS "Deposit", 
        COALESCE(pd."Booking_fee", 0) AS "Booking_fee"
      FROM "Resource"."Resource" r
        INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
        INNER JOIN "Billing"."Pricing_rate" pr ON r."Rate_id"  = pr.id
        INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
        INNER JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
        INNER JOIN "Billing"."Pricing_detail" pd ON (pd."Building_id" = b.id AND pd."Flat_type_id" = rft.id AND pd."Place_type_id" = rpt.id)
      WHERE pd."Year" = %s
        AND b.id = %s
        AND rpt.id = %s
        AND rft.id = %s
      LIMIT 1
      '''

  try:
    dbClient.connect()
    dbClient.select(sql, (year, building_id, place_type_id, flat_type_id))
    results = dbClient.fetchall()
    dbClient.disconnect()
    if len(results) > 0:
      return results[0]
    return None
 
  except Exception as error:
    logger.error(error)
    dbClient.rollback()
    return None
 
# ------------------------------------------------------
# Create customer
# ------------------------------------------------------

def q_insert_customer(dbClient, customer):

  # SQL
  sql = f'''
    INSERT INTO "Customer"."Customer"
    ("Type", "Name", "Email", "Phones", "Birth_date", "Nationality_id", "Gender_id", "Black_list")
    VALUES ('persona', %s, %s, %s, %s, %s, %s, FALSE)
    RETURNING id
    '''
  try:
    dbClient.connect()
    dbClient.execute(sql, (
      customer['Name'], 
      customer['Email'], 
      customer['Phones'], 
      customer['Birth_date'], 
      customer['Nationality_id'], 
      customer['Gender_id'], 
    ))
    id = dbClient.returning()[0]
    dbClient.commit()
    dbClient.disconnect()
    return id, None
 
  except Exception as error:
    logger.error(error)
    dbClient.rollback()
    return None, error

# ------------------------------------------------------
# Create booking
# ------------------------------------------------------

def q_insert_booking(dbClient, booking):

  # SQL
  sql = f'''
    INSERT INTO "Booking"."Booking" (
      "Date_from", "Date_to", "Customer_id", "Building_id", 
      "Resource_type", "Flat_type_id", "Place_type_id", "Reason_id", "Comments", 
      "Booking_channel_id", "Second_resident", "Lock"
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1, FALSE, FALSE)
    RETURNING id
    '''
  try:
    dbClient.connect()
    dbClient.execute(sql, (
      booking["Date_from"],
      booking["Date_to"],
      booking["Customer_id"],
      booking["Building_id"],
      booking["Resource_type"],
      booking["Flat_type_id"],
      booking["Place_type_id"],
      booking["Reason_id"],
      booking["Comments"]
    ))
    id = dbClient.returning()[0]
    dbClient.commit()
    dbClient.disconnect()
    return id, None
 
  except Exception as error:
    logger.error(error)
    dbClient.rollback()
    return None, error

# ------------------------------------------------------
# Availability for static web
# ------------------------------------------------------

def q_availability(dbClient, type, filter, date_from, date_to):

  # Connect
  try:
    dbClient.connect()

    # Single, Shared and Flat availabilities for all buildings
    if type == 0:
      sql = '''
        SELECT 
          CONCAT(r."Building_id", '_', SUBSTRING(rpt."Code", 1, 1)) as "id", COUNT(*) as "Qty"
        FROM
          "Resource"."Resource" r
          INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
          LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
          LEFT JOIN "Booking"."Booking_detail" bd ON (bd."Resource_id" = r.id AND bd."Date_from" <= %s AND bd."Date_to" >= %s)
        WHERE rpt."Code" NOT LIKE 'DUI%%'
          AND r."Sale_type" IN ('plazas', 'ambos')
          AND bd.id IS NULL
        GROUP BY 1  
        UNION
        SELECT 
          CONCAT(r."Building_id", '_F') as "id", COUNT(*) as "Qty"
        FROM
          "Resource"."Resource" r
          INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
          LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
          LEFT JOIN "Booking"."Booking_detail" bd ON (bd."Resource_id" = r.id AND bd."Date_from" <= %s AND bd."Date_to" >= %s)
        WHERE rpt."Code" IS NULL
          AND r."Sale_type" IN ('completo', 'ambos')
          AND bd.id IS NULL
        GROUP BY 1
      '''
      dbClient.select(sql, (date_to, date_from, date_to, date_from))

    # Room availabilities for one building
    elif type == 1:
      sql = '''
        SELECT 
          CONCAT(rpt."Code", '_', rft."Code") AS "id", COUNT(*) AS "Qty"
        FROM
          "Resource"."Resource" r
          INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
          LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
          LEFT JOIN "Booking"."Booking_detail" bd ON (bd."Resource_id" = r.id AND bd."Date_from" <= %s AND bd."Date_to" >= %s)
        WHERE bd.id IS NULL 
          AND r."Building_id" = %s 
          AND rpt."Code" NOT LIKE 'DUI%%'
          AND r."Sale_type" IN ('plazas', 'ambos')
        GROUP BY 1
        '''
      dbClient.select(sql, (date_to, date_from, filter))

    # Flat availabilities for one building
    else:
      sql = '''
        SELECT 
          rfst."Code" AS "id", COUNT(*) AS "Qty"
        FROM
          "Resource"."Resource" r
          INNER JOIN "Resource"."Resource_flat_subtype" rfst ON rfst.id = r."Flat_subtype_id"
          LEFT JOIN "Booking"."Booking_detail" bd ON (bd."Resource_id" = r.id AND bd."Date_from" <= %s AND bd."Date_to" >= %s)
        WHERE bd.id IS NULL 
          AND r."Building_id" = %s
          AND r."Sale_type" IN ('completo', 'ambos')
        GROUP BY 1
        '''
      dbClient.select(sql, (date_to, date_from, filter))

    # Read data
    column_names = [desc[0] for desc in dbClient.sel.description]
    result = [{col: (row[i] if row[i] is not None else '') for i, col in enumerate(column_names)} for row in dbClient.fetchall()]
    dbClient.disconnect()
    return result

  except Exception as error:
    logger.error(error)
    dbClient.rollback()
    return []