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
def month_dates(date_from, date_to, price, price_next, lang):

  df = datetime.strptime(date_from, "%Y-%m-%d")
  dt = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
  d = month(df.month, lang).capitalize()[:3] + ' ' + str(df.year)
  dates = [{'date': d, 'd':df.date(), 'price': 0, 'rack': 0}]
  next = (df.replace(day=1) + relativedelta(months=1))
  while next <= dt:
    if df.month != next.month and next.month == 9:
      price = price_next
    d = month(next.month, lang).capitalize()[:3] + ' ' + str(next.year)
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
  first_year = df.year if df.month < 9 else df.year + 1
  last_year  = dt.year if dt.month < 9 else dt.year + 1

  # Return
  return first_year, last_year, field


# ######################################################
# Booking queries
# ######################################################

# ------------------------------------------------------
# Generic query
# ------------------------------------------------------

def q(dbClient, sql, params):

  con = None
  try:
    con = dbClient.getconn()
    cur = dbClient.execute(con, sql, params)
    result = [dict(row) for row in cur.fetchall()]
    cur.close()
    return result

  except Exception as error:
    logger.error(error)
    if con:
      con.rollback()
    return None

  finally:
    dbClient.putconn(con)


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
# Get id types
# ------------------------------------------------------

def q_id_types(dbClient, lang):

  # Id types query
  l = '_en' if lang == 'en' else ''
  return q(dbClient, f'SELECT id, "Name{l}" AS "Name" FROM "Auxiliar"."Id_type"', ())
 

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
        WHEN rpt."Code" LIKE 'I\\_%%' THEN 'ind'
        WHEN rpt."Code" LIKE 'D\\_%%' THEN 'sha'
        WHEN rpt."Code" LIKE 'DUI\\_%%' THEN 'idu'
        ELSE 'apt'
      END as "Room_type",
      COUNT(*)
    FROM "Resource"."Resource" r
      INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
      INNER JOIN "Geo"."District" d on d.id = b."District_id"
      INNER JOIN "Geo"."Location" l on l.id = d."Location_id"
      LEFT JOIN "Resource"."Resource" f on f.id = r."Flat_id"
      LEFT JOIN "Resource"."Resource_place_type" rpt on rpt.id = r."Place_type_id"
    WHERE b."Building_type_id" < 4
      AND b."Active" 
      AND CASE WHEN r."Resource_type" = 'piso' THEN r."Segment_id" ELSE f."Segment_id" END = %s
      AND r."Sale_type" IS NOT NULL
      --AND (rpt."Code" IS NULL OR rpt."Code" NOT LIKE 'DUI_%%')
    GROUP BY 1, 2, 3, 4
    ORDER BY 1, 2, 3, 4
    '''

  con = None
  try:

    # Read data
    con = dbClient.getconn()
    cur = dbClient.execute(con, sql, (segment, ))
    data = cur.fetchall()
    cur.close()

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
    if con:
      con.rollback()
    return None

  finally:
    dbClient.putconn(con)

# ------------------------------------------------------
# Search results
# ------------------------------------------------------

def q_book_search(dbClient, segment, lang, date_from, date_to, city, acom_type, room_type):
 
  # Query parameters
  l = '_en' if lang == 'en' else ''
  first_year, last_year, field = rent_info(date_from, date_to)
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
        AND r."Segment_id" = %s
        AND b."Building_type_id" < 3
        AND d."Location_id" = %s
      GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
      '''
    params = (date_to, date_from, first_year, segment, city, )
  else:
    sql = f'''
      SELECT
        b.id as "Building_id", rpt.id AS "Place_type_id", rft.id AS "Flat_type_id",
        b."Code" AS "Building_code", rpt."Code" AS "Place_type_code", rft."Code" AS "Flat_type_code",
        b."Name" as "Building_name", rpt."Name{l}" AS "Place_type_name", rft."Name{l}" AS "Flat_type_name",
        pd."Services" + ROUND(pr."Multiplier" * pd."{field}", 0) AS "Price", MIN(mrt.id) AS "Photo"
      FROM "Resource"."Resource" r
        INNER JOIN "Resource"."Resource" f ON f.id = r."Flat_id"
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
        AND f."Segment_id" = %s
        AND b."Building_type_id" IN %s
        AND d."Location_id" = %s
        AND rpt."Code" LIKE %s
      GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
      '''
    params = (date_to, date_from, first_year, segment, building_type, city, place_type, )

  con = None
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
    return sorted(grouped_data, key=lambda x: x['Price'])

  except Exception as error:
    logger.error(error)
    if con:
      con.rollback()
    return None

  finally:
    dbClient.putconn(con)


# ------------------------------------------------------
# Get summary
# ------------------------------------------------------

def q_book_summary(dbClient, lang, date_from, date_to, building_id, place_type_id, flat_type_id, acom_type):

  # Query parameters
  l = '_en' if lang == 'en' else ''
  first_year, last_year, field = rent_info(date_from, date_to)

  # Private aparment
  if acom_type == 'ap':
    sql = f'''
      SELECT DISTINCT
        b."Name" as "Building_name", b."Code" AS "Building_code", d."Location_id",
        rfst."Name{l}" AS "Place_type_name", NULL AS "Place_type_code",
        rft."Name{l}" AS "Flat_type_name",
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
        INNER JOIN "Geo"."District" d ON d.id = b."District_id"
        INNER JOIN "Billing"."Pricing_rate" pr ON r."Rate_id"  = pr.id
        INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
        INNER JOIN "Resource"."Resource_flat_subtype" rfst ON rfst.id = r."Flat_subtype_id"
        INNER JOIN "Billing"."Pricing_detail" pd ON (pd."Building_id" = b.id AND pd."Flat_type_id" = rft.id)
      WHERE (pd."Year" = %s or pd."Year" = %s)
        AND b.id = %s
        AND rft.id = %s
        AND rfst.id = %s
      LIMIT 2
      '''
  else:
    sql = f'''
      SELECT DISTINCT
        b."Name" as "Building_name", b."Code" AS "Building_code", d."Location_id",
        rpt."Name{l}" AS "Place_type_name", rpt."Code" AS "Place_type_code",
        rft."Name{l}" AS "Flat_type_name",
        r."Billing_type",
        ROUND(pr."Multiplier" * COALESCE(pd."{field}", 0), 0) AS "Rent",
        COALESCE(pd."Services", 0) AS "Services",
        COALESCE(pd."Limit", 0) as "Limit",
        COALESCE(pd."Deposit", 0) AS "Deposit",
        COALESCE(pd."Booking_fee", 0) AS "Booking_fee",
        COALESCE(pd."Final_cleaning", 0) AS "Final_cleaning"
      FROM "Resource"."Resource" r
        INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
        INNER JOIN "Geo"."District" d ON d.id = b."District_id"
        INNER JOIN "Billing"."Pricing_rate" pr ON r."Rate_id"  = pr.id
        INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
        INNER JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
        INNER JOIN "Billing"."Pricing_detail" pd ON (pd."Building_id" = b.id AND pd."Flat_type_id" = rft.id AND pd."Place_type_id" = rpt.id)
      WHERE (pd."Year" = %s or pd."Year" = %s)
        AND b.id = %s
        AND rft.id = %s
        AND rpt.id = %s
      LIMIT 2
      '''

  con = None
  try:
    # Get data
    con = dbClient.getconn()
    cur = dbClient.execute(con, sql, (first_year, first_year + 1, building_id, flat_type_id, place_type_id))
    results = [dict(row) for row in cur.fetchall()]
    cur.close()

    # Two years span
    if first_year < last_year:
      if len(results) < 2:
        return None
      first = results[0]
      last = results[1]

    # One year span
    else:
      if len(results) < 1:
        return None
      first = results[0]
      last = results[0]
    
    # Preset first and last month prices
    first['Rent_first'] = first['Rent']
    first['Rent_last']  = last['Rent']

    # Day and total days of 1st and last months
    dayf, daysf = days(date_from) 
    dayt, dayst = days(date_to)

    # Adjust prices if proportional
    if first['Billing_type'] == 'proporcional':
      first['Rent_first'] = first['Rent_first'] * (daysf - dayf) / daysf
      first['Rent_last'] = first['Rent_last'] * dayt / dayst

    # Adjust prices if by fortnights
    elif first['Billing_type'] == 'quincena':
      if dayf >= 15:
        first['Rent_first'] = first['Rent_first'] / 2
      if dayt < 15:
        first['Rent_last'] = first['Rent_last'] / 2

    # Details
    months = month_dates(date_from, date_to, float(first['Rent']) + float(first['Services']), float(last['Rent']) + float(last['Services']), lang)
    months[0]['price'] = float(first['Rent_first']) + float(first['Services'])
    months[0]['rack'] = float(first['Rent_first']) + float(first['Services'])
    months[-1]['price'] = float(first['Rent_last']) + float(last['Services'])
    months[-1]['rack'] = float(first['Rent_last']) + float(last['Services'])

    # Get promotion
    sql = '''
      SELECT *
      FROM "Billing"."Promotion" p
      WHERE p."Date_from" <= %s 
        AND p."Date_to" >= %s
        AND p."Active_from" <= CURRENT_DATE
        AND p."Active_to" >= CURRENT_DATE
        AND (
          NOT EXISTS (
            SELECT 1
            FROM "Billing"."Promotion_building" pb0
            WHERE pb0."Promotion_id" = p.id
          )
          OR EXISTS (
            SELECT 1
            FROM "Billing"."Promotion_building" pb
            WHERE pb."Promotion_id" = p.id
              AND pb."Building_id"  = %s
          )
        )
        AND (
          NOT EXISTS (
            SELECT 1
            FROM "Billing"."Promotion_place" pp0
            WHERE pp0."Promotion_id" = p.id
          )
          OR EXISTS (
            SELECT 1
            FROM "Billing"."Promotion_place" pp
            WHERE pp."Promotion_id" = p.id
              AND (pp."Flat_type_id"  IS NULL OR pp."Flat_type_id"  = %s)
              AND (pp."Place_type_id" IS NULL OR pp."Place_type_id" = %s)
          )
        )
      ORDER BY id DESC
      LIMIT 1;
    '''
    cur = dbClient.execute(con, sql, (date_to, date_from, building_id, flat_type_id, place_type_id))
    promos = [dict(row) for row in cur.fetchall()]
    cur.close()

    # Convert and return data
    first['Booking_fee'] = float(first['Booking_fee'])
    first['Booking_fee_rack'] = float(first['Booking_fee'])
    first['Deposit'] = float(first['Deposit'])
    first['Rent'] = float(first['Rent'])
    first['Rent_first'] = float(first['Rent_first'])
    first['Rent_last'] = float(first['Rent_last'])
    first['Services'] = float(first['Services'])
    first['Final_cleaning'] = float(first['Final_cleaning'])
    first['Months'] = months

    # Apply promotion
    if len(promos):
      promo = promos[0]
      if promo['Value_fee']:
        first['Booking_fee'] += float(promo['Value_fee'])
      elif promo['Value_fee_pct']:
        first['Booking_fee'] *= (1.0 + float(promo['Value_fee_pct'] / 100))
      for m in months:
        if promo['Date_from'] <= m['d'] <= promo['Date_to']:
          if promo['Value_rent']:
            m['price'] += float(promo['Value_rent'])
          elif promo['Value_rent_pct']:
            m['price'] *= (1.0 + float(promo['Value_rent_pct'] / 100))
          m['price'] = round(m['price'])

    # Totals
    total_price = 0
    total_rack  = 0
    for m in months:
      total_price += m['price']
      total_rack  += m['rack']
    first['Total']      = total_price
    first['Total_rack'] = total_rack

    # Returl
    return first

  except Exception as error:
    logger.error(error)
    if con:
      con.rollback()
    return None

  finally:
    dbClient.putconn(con)


# ------------------------------------------------------
# Create customer
# ------------------------------------------------------

def q_insert_customer(dbClient, customer):

  # SQL
  sql = f'''
    INSERT INTO "Customer"."Customer"
    ("Type", "Name", "Email", "Phones", "Birth_date", "Nationality_id", "Gender_id",
     "Tutor_id_type_id", "Tutor_document", "Tutor_name", "Tutor_email", "Tutor_phones", 
     "Black_list", "GDPR")
    VALUES ('persona', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE, TRUE)
    RETURNING id
    '''
  con = None
  try:
    con = dbClient.getconn()
    cur = dbClient.execute(con, sql, (
      customer['Name'],
      customer['Email'], 
      customer['Phones'], 
      customer['Birth_date'], 
      customer['Nationality_id'], 
      customer['Gender_id'], 
      customer['Tutor_id_type_id'],
      customer['Tutor_document'],
      customer['Tutor_name'],
      customer['Tutor_email'],
      customer['Tutor_phones']))
    id = cur.fetchone()[0]
    con.commit()
    return id, None

  except Exception as error:
    logger.error(error)
    if con:
      con.rollback()
    return None, error

  finally:
    dbClient.putconn(con)

# ------------------------------------------------------
# Create booking
# ------------------------------------------------------

def q_insert_booking(dbClient, booking):

  con = None
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
    return id, None

  except Exception as error:
    logger.error(error)
    if con:
      con.rollback()
    return None, error

  finally:
    dbClient.putconn(con)

# ------------------------------------------------------
# Availability for static web
# ------------------------------------------------------

def q_availability(dbClient, type, filter, date_from, date_to, segment):

  # Filtro de marca. Las plazas siguen al piso padre (f), los pisos van por su
  # propia columna (r). Sin segmento no se filtra: las webs publicadas que aun
  # no mandan el parametro siguen viendo el total como hasta ahora
  seg_flat  = 'AND f."Segment_id" = %s' if segment is not None else ''
  seg_own   = 'AND r."Segment_id" = %s' if segment is not None else ''
  seg_param = [segment] if segment is not None else []

  # Connect
  con = None
  try:
    con = dbClient.getconn()

    # Single, Shared and Flat availabilities for all buildings
    if type == 0:
      sql = f'''
        SELECT 
          CONCAT(r."Building_id", '_', SUBSTRING(rpt."Code", 1, 1)) as "id", COUNT(*) as "Qty"
        FROM
          "Resource"."Resource" r
          INNER JOIN "Resource"."Resource" f ON f.id = r."Flat_id"
          INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
          INNER JOIN "Geo"."District" d ON d.id = b."District_id"
          INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
          LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
          LEFT JOIN "Booking"."Booking_detail" bd ON (bd."Resource_id" = r.id AND bd."Date_from" <= %s AND bd."Date_to" >= %s)
        WHERE r."Sale_type" IN ('plazas', 'ambos')
          --AND rpt."Code" NOT LIKE 'DUI%%'
          AND (d."Location_id" <> 1 OR b."Building_type_id" = 3)
          {seg_flat}
          AND bd.id IS NULL
        GROUP BY 1  
        UNION ALL
        SELECT 
          CONCAT(r."Building_id", '_F') as "id", COUNT(*) as "Qty"
        FROM
          "Resource"."Resource" r
          INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
          INNER JOIN "Geo"."District" d ON d.id = b."District_id"
          INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
          LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
          LEFT JOIN "Booking"."Booking_detail" bd ON (bd."Resource_id" = r.id AND bd."Date_from" <= %s AND bd."Date_to" >= %s)
        WHERE rpt."Code" IS NULL
          AND r."Sale_type" IN ('completo', 'ambos')
          {seg_own}
          AND bd.id IS NULL
        GROUP BY 1
      '''
      cur = dbClient.execute(con, sql, [date_to, date_from] + seg_param + [date_to, date_from] + seg_param)

    # Room cur for one building
    elif type == 1:
      sql = f'''
        SELECT 
          CONCAT(rpt."Code", '_', rft."Code") AS "id", COUNT(*) AS "Qty"
        FROM
          "Resource"."Resource" r
          INNER JOIN "Resource"."Resource" f ON f.id = r."Flat_id"
          INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
          INNER JOIN "Geo"."District" d ON d.id = b."District_id"
          INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
          LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
          LEFT JOIN "Booking"."Booking_detail" bd ON (bd."Resource_id" = r.id AND bd."Date_from" <= %s AND bd."Date_to" >= %s)
        WHERE bd.id IS NULL 
          --AND rpt."Code" NOT LIKE 'DUI%%'
          AND r."Building_id" = %s 
          {seg_flat}
          AND r."Sale_type" IN ('plazas', 'ambos')
        GROUP BY 1
        '''
      cur = dbClient.execute(con, sql, [date_to, date_from, filter] + seg_param)

    # Flat cur for one building
    else:
      sql = f'''
        SELECT 
          rfst."Code" AS "id", COUNT(*) AS "Qty"
        FROM
          "Resource"."Resource" r
          INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
          INNER JOIN "Geo"."District" d ON d.id = b."District_id"
          INNER JOIN "Resource"."Resource_flat_subtype" rfst ON rfst.id = r."Flat_subtype_id"
          LEFT JOIN "Booking"."Booking_detail" bd ON (bd."Resource_id" = r.id AND bd."Date_from" <= %s AND bd."Date_to" >= %s)
        WHERE bd.id IS NULL 
          AND r."Building_id" = %s
          {seg_own}
          AND r."Sale_type" IN ('completo', 'ambos')
        GROUP BY 1
        '''
      cur = dbClient.execute(con, sql, [date_to, date_from, filter] + seg_param)

    # Read cur
    column_names = [desc[0] for desc in cur.description]
    result = [{col: (row[i] if row[i] is not None else '') for i, col in enumerate(column_names)} for row in cur.fetchall()]
    cur.close()
    return result

  except Exception as error:
    logger.error(error)
    if con:
      con.rollback()
    return []

  finally:
    dbClient.putconn(con)