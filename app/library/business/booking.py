# ######################################################
# Imports
# ######################################################

# System includes
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from calendar import monthrange

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ######################################################
# Misc functions
# ######################################################

# Month name
def month(m, lang='es'):

  try:
    if lang == 'es':
      return ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'][m-1]
    else:
      return ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][m-1]
  except:
    return '--'


# List of months (MMM YYYY) between two dates
def month_dates(date_from, date_to, price):

  df = datetime.strptime(date_from, "%Y-%m-%d")
  dt = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
  d = month(df.month).capitalize()[:3] + ' ' + str(df.year)
  dates = [{'date': d, 'd':df.date(), 'price': 0, 'rack': 0}]
  next = (df.replace(day=1) + relativedelta(months=1))
  while next <= dt:
    d = month(next.month).capitalize()[:3] + ' ' + str(next.year)
    dates.append({ 'date': d, 'd': next.date(), 'price': price, 'rack': price })
    next += relativedelta(months=1)
  return dates


# Num. of the day of a date and num. of days of that month
def days(date):

  d = datetime.strptime(date, "%Y-%m-%d")
  days = monthrange(d.year, d.month)[1]
  return d.day, days


def rent_info(date_from, date_to):

  # Calculate length type
  df = datetime.strptime(date_from, "%Y-%m-%d")
  dt = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
  difference = relativedelta(dt, df)
  months = difference.years * 12 + difference.months
  if months < 3:
    field = 'Rent_short'
  elif months < 7:
    field = 'Rent_medium'
  else:
    field = 'Rent_long'

  # Rates year
  year = df.year if df.month < 9 else df.year + 1

  # Return
  return year, field


# ######################################################
# Booking queries
# ######################################################

# ------------------------------------------------------
# Generic query
# ------------------------------------------------------

def q(dbClient, sql, params):

  try:
    con = dbClient.getconn()
    cur = dbClient.execute(con, sql, params)
    result = [dict(row) for row in cur.fetchall()]
    cur.close()
    dbClient.putconn(con)
    return result
 
  except Exception as error:
    logger.error(error)
    con.rollback()
    dbClient.putconn(con)
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
# Get Schools
# ------------------------------------------------------

def q_schools(dbClient, lang):

  # Schools query
  return q(dbClient, f'SELECT id, "Name" FROM "Auxiliar"."School" WHERE id > 1 ORDER BY 2', ())
 

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
    con = dbClient.getconn()
    cur = dbClient.execute(con, sql)
    data = cur.fetchall()
    cur.close()
    dbClient.putconn(con)

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
    con.rollback()
    dbClient.putconn(con)
    return None

# ------------------------------------------------------
# Search results
# ------------------------------------------------------

def q_book_search(dbClient, segment, lang, date_from, date_to, city, acom_type, room_type):
 
  # Query parameters
  l = '_en' if lang == 'en' else ''
  year, field = rent_info(date_from, date_to)
  place_type = 'I_%' if room_type == 'ind' else 'D_%'
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
        AND r."Sale_type" IN ('ambos', 'completo')
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
        AND r."Sale_type" IN ('ambos', 'plazas')
        AND pd."Year" = %s
        AND b."Segment_id" = %s
        AND b."Building_type_id" IN %s
        AND d."Location_id" = %s
        AND rpt."Code" LIKE %s
      GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
      '''
    params = (date_to, date_from, year, segment, building_type, city, place_type, )

  try:
    con = dbClient.getconn()
    cur = dbClient.execute(con, sql, params)
    results = cur.fetchall()
    cur.close()
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
    dbClient.putconn(con)
    return sorted(grouped_data, key=lambda x: x['Price'])
 
  except Exception as error:
    logger.error(error)
    con.rollback()
    dbClient.putconn(con)
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
        r."Billing_type",
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
        AND rft.id = %s
        AND rfst.id = %s
      LIMIT 1
      '''
  else:
    sql = f'''
      SELECT DISTINCT
        b."Name" as "Building_name", rpt."Name{l}" AS "Place_type_name", rft."Name{l}" AS "Flat_type_name",
        r."Billing_type",
        ROUND(pr."Multiplier" * COALESCE(pd."{field}", 0), 0) AS "Rent",
        COALESCE(pd."Services", 0) AS "Services", 
        COALESCE(pd."Limit", 0) as "Limit",
        COALESCE(pd."Deposit", 0) AS "Deposit", 
        COALESCE(pd."Booking_fee", 0) AS "Booking_fee",
        COALESCE(pd."Final_cleaning", 0) AS "Final_cleaning"
      FROM "Resource"."Resource" r
        INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
        INNER JOIN "Billing"."Pricing_rate" pr ON r."Rate_id"  = pr.id
        INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
        INNER JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
        INNER JOIN "Billing"."Pricing_detail" pd ON (pd."Building_id" = b.id AND pd."Flat_type_id" = rft.id AND pd."Place_type_id" = rpt.id)
      WHERE pd."Year" = %s
        AND b.id = %s
        AND rft.id = %s
        AND rpt.id = %s
      LIMIT 1
      '''

  try:
    # Get data
    con = dbClient.getconn()
    cur = dbClient.execute(con, sql, (year, building_id, flat_type_id, place_type_id))
    results = [dict(row) for row in cur.fetchall()]
    cur.close()
    if len(results) < 1:
      dbClient.putconn(con)
      return None
    
    # Preset first and last month prices
    data = results[0]
    data['Rent_first'] = data['Rent']
    data['Rent_last'] = data['Rent']

    # Day and total days of 1st and last months
    dayf, daysf = days(date_from) 
    dayt, dayst = days(date_to)

    # Adjust prices if proportional
    if data['Billing_type'] == 'proporcional':
      data['Rent_first'] = data['Rent'] * (daysf - dayf) / daysf
      data['Rent_last'] = data['Rent'] * dayt / dayst

    # Adjust prices if by fortnights
    elif data['Billing_type'] == 'quincena':
      if dayf >= 15:
        data['Rent_first'] = data['Rent'] / 2
      if dayt < 15:
        data['Rent_last'] = data['Rent'] / 2

    # Details
    months = month_dates(date_from, date_to, float(data['Rent']) + float(data['Services']))
    months[0]['price'] = float(data['Rent_first']) + float(data['Services'])
    months[0]['rack'] = float(data['Rent_first']) + float(data['Services'])
    months[-1]['price'] = float(data['Rent_last']) + float(data['Services'])
    months[-1]['rack'] = float(data['Rent_last']) + float(data['Services'])

    # Get promotion
    sql = '''
      SELECT *
      FROM "Billing"."Promotion" p
      WHERE p."Building_id" = %s
        AND (p."Flat_type_id" IS NULL OR p."Flat_type_id" = %s)
        AND (p."Place_type_id" IS NULL OR p."Place_type_id" = %s)
        AND p."Date_from" <= %s 
        AND p."Date_to" >= %s
        AND p."Active_from" <= CURRENT_DATE
        AND p."Active_to" >= CURRENT_DATE
      ORDER BY id DESC
      LIMIT 1;
    '''
    cur = dbClient.execute(con, sql, (building_id, flat_type_id, place_type_id, date_to, date_from))
    promos = [dict(row) for row in cur.fetchall()]
    cur.close()

    # Convert and return data
    data['Booking_fee'] = float(data['Booking_fee'])
    data['Booking_fee_rack'] = float(data['Booking_fee'])
    data['Deposit'] = float(data['Deposit'])
    data['Rent'] = float(data['Rent'])
    data['Rent_first'] = float(data['Rent_first'])
    data['Rent_last'] = float(data['Rent_last'])
    data['Services'] = float(data['Services'])
    data['Final_cleaning'] = float(data['Final_cleaning'])
    data['Months'] = months

    # Apply promotion
    if len(promos):
      promo = promos[0]
      if promo['Value_fee']:
        data['Booking_fee'] += float(promo['Value_fee'])
      elif promo['Value_fee_pct']:
        data['Booking_fee'] *= (1.0 + float(promo['Value_fee_pct'] / 100))
      for m in months:
        print(m['d'])
        if promo['Date_from'] <= m['d'] <= promo['Date_to']:
          if promo['Value_rent']:
            m['price'] += float(promo['Value_rent'])
          elif promo['Value_rent_pct']:
            m['price'] *= (1.0 + float(promo['Value_rent_pct'] / 100))

    # Total
    total = 0
    for m in months:
      total += m['price']
    data['Total'] = total

    # Returl
    dbClient.putconn(con)
    return data
 
  except Exception as error:
    logger.error(error)
    con.rollback()
    dbClient.putconn(con)
    return None
 
# ------------------------------------------------------
# Create customer
# ------------------------------------------------------

def q_insert_customer(dbClient, customer):

  # SQL
  sql = f'''
    INSERT INTO "Customer"."Customer"
    ("Type", "Name", "Email", "Phones", "Birth_date", "Nationality_id", "Gender_id", "Black_list", "GDPR")
    VALUES ('persona', %s, %s, %s, %s, %s, %s, FALSE, TRUE)
    RETURNING id
    '''
  try:
    con = dbClient.getconn()
    cur = dbClient.execute(con, sql, (
      customer['Name'], 
      customer['Email'], 
      customer['Phones'], 
      customer['Birth_date'], 
      customer['Nationality_id'], 
      customer['Gender_id'], 
    ))
    id = cur.fetchone()[0]
    con.commit()
    dbClient.putconn(con)
    return id, None
 
  except Exception as error:
    logger.error(error)
    con.rollback()
    dbClient.putconn(con)
    return None, error

# ------------------------------------------------------
# Create booking
# ------------------------------------------------------

def q_insert_booking(dbClient, booking):

  try:
    # Get connection
    con = dbClient.getconn()

    # Check if exists
    sql = f'''
      SELECT id 
      FROM "Booking"."Booking"
      WHERE "Date_from" = %s
        AND "Date_to" = %s
        AND "Customer_id" = %s
        AND "Building_id" = %s
        AND "Resource_type" = %s
        AND "Flat_type_id" = %s
        AND "Place_type_id" = %s
      LIMIT 1
    '''
    cur = dbClient.execute(con, sql, (
      booking["Date_from"],
      booking["Date_to"],
      booking["Customer_id"],
      booking["Building_id"],
      booking["Resource_type"],
      booking["Flat_type_id"],
      booking["Place_type_id"]
    ))
    id = cur.fetchone()
    if id:
      cur.close()
      dbClient.putconn(con)
      return id[0], None
  
    # SQL
    sql = f'''
      INSERT INTO "Booking"."Booking" (
        "Date_from", "Date_to", "Customer_id", "Building_id", 
        "Resource_type", "Flat_type_id", "Place_type_id", "Reason_id", "School_id", "Other_school", "Company", "Comments", 
        "Booking_channel_id", "Second_resident", "Lock"
      )
      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, FALSE, FALSE)
      RETURNING id
    '''
    cur = dbClient.execute(con, sql, (
      booking["Date_from"],
      booking["Date_to"],
      booking["Customer_id"],
      booking["Building_id"],
      booking["Resource_type"],
      booking["Flat_type_id"],
      booking["Place_type_id"],
      booking["Reason_id"],
      booking["School_id"],
      booking["Other_school"],
      booking["Company"],
      booking["Comments"]
    ))
    id = cur.fetchone()[0]
    con.commit()
    cur.close()
    dbClient.putconn(con)
    return id, None
 
  except Exception as error:
    logger.error(error)
    con.rollback()
    dbClient.putconn(con)
    return None, error

# ------------------------------------------------------
# Availability for static web
# ------------------------------------------------------

def q_availability(dbClient, type, filter, date_from, date_to):

  # Connect
  try:
    con = dbClient.getconn()

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
        UNION ALL
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
      cur = dbClient.execute(con, sql, (date_to, date_from, date_to, date_from))

    # Room cur for one building
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
      cur = dbClient.execute(con, sql, (date_to, date_from, filter))

    # Flat cur for one building
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
      cur = dbClient.execute(con, sql, (date_to, date_from, filter))

    # Read cur
    column_names = [desc[0] for desc in cur.description]
    result = [{col: (row[i] if row[i] is not None else '') for i, col in enumerate(column_names)} for row in cur.fetchall()]
    cur.close()
    dbClient.putconn(con)
    return result

  except Exception as error:
    logger.error(error)
    con.rollback()
    dbClient.putconn(con)
    return []