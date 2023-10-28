# ######################################################
# Imports
# ######################################################

# System includes
from datetime import datetime
from dateutil import relativedelta
import json

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ######################################################
# Booking process
# ######################################################

# Get information of existing typologies
def typologies(dbClient, segment):

  # SQL 
  sql = '''
    SELECT l.id, l."Name", 
      CASE 
        WHEN b."Building_type_id" = 3 THEN 'rs'
        WHEN (r."Sale_type" = 'ambos' OR r."Sale_type" = 'plazas') THEN 'pc'
        WHEN (r."Sale_type" = 'ambos' OR r."Sale_type" = 'completo') THEN 'ap'
      END as "Sale_type",
      CASE 
        WHEN rpt."Code" LIKE 'I_%' THEN 'ind'
        WHEN rpt."Code" LIKE 'D_%' THEN 'sha'
      END as "Room_type",
      COUNT(*)
    FROM "Resource"."Resource" r
      INNER JOIN "Building"."Building" b ON b.id = r."Building_id" 
      INNER JOIN "Geo"."District" d on d.id = b."District_id" 
      INNER JOIN "Geo"."Location" l on l.id = d."Location_id" 
      LEFT JOIN "Resource"."Resource_place_type" rpt on rpt.id = r."Place_type_id" 
    WHERE b."Building_type_id" < 4
      AND b."Segment_id" = {}
      AND "Sale_type" IS NOT NULL
      AND rpt."Code" NOT LIKE 'DUI_%'
    GROUP BY 1, 2, 3, 4
    ORDER BY 1, 2, 3
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
    return None

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


# Get available typologies between dates
def available_rooms(dbClient, segment, lang, date_from, date_to, city, acom, room):
  
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

  # Search parameters
  l = '_en' if lang == 'en' else ''
  year = df.year if df.month < 9 else df.year + 1
  place_type = 'I_%' if room == 'ind' else 'D\_%'
  building_type = (3,) if acom == 'rs' else (1, 2)

  # Rooms
  if acom == 'ap':
    sql = f'''
      SELECT 
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
        INNER JOIN "Marketing"."Media_resource_type" mrt ON (mrt."Building_id" = b.id AND mrt."Flat_subtype_id" = rfst.id)
        LEFT JOIN "Booking"."Booking_detail" bd ON (bd."Resource_id" = r.id AND bd."Date_from" <= %s AND bd."Date_to" >= %s)
      WHERE bd.id IS NULL 
        AND b."Segment_id" = %s
        AND pd."Year" = %s
        AND b."Building_type_id" < 3
        AND d."Location_id" = %s
      GROUP BY 1, 2, 3, 4, 5, 6, 7
      '''
    params = (date_to, date_from, segment, year, city, )
  else:
    sql = f'''
      SELECT 
        b."Code" as "Building_code", rpt."Code" AS "Place_type_code", rft."Code" AS "Flat_type_code", 
        b."Name" as "Building_name", rpt."Name{l}" AS "Place_type_name", rft."Name{l}" AS "Flat_type_name", 
        ROUND(pd."Services" + pr."Multiplier" * pd."{field}", 0) AS "Price", MIN(mrt.id) AS "Photo"
      FROM "Resource"."Resource" r
        INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
        INNER JOIN "Geo"."District" d ON d.id = b."District_id" 
        INNER JOIN "Billing"."Pricing_rate" pr ON r."Rate_id"  = pr.id
        INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id" 
        INNER JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id" 
        INNER JOIN "Billing"."Pricing_detail" pd ON (pd."Building_id" = b.id AND pd."Flat_type_id" = rft.id AND pd."Place_type_id" = rpt.id)
        INNER JOIN "Marketing"."Media_resource_type" mrt ON (mrt."Building_id" = b.id AND mrt."Place_type_id" = rpt.id)
        LEFT JOIN "Booking"."Booking_detail" bd ON (bd."Resource_id" = r.id AND bd."Date_from" <= %s AND bd."Date_to" >= %s)
      WHERE bd.id IS NULL 
        AND b."Segment_id" = %s
        AND pd."Year" = %s 
        AND b."Building_type_id" IN %s
        AND d."Location_id" = %s
        AND rpt."Code" LIKE %s
      GROUP BY 1, 2, 3, 4, 5, 6, 7
      '''
    params = (date_to, date_from, segment, year, building_type, city, place_type, )

  try:
    dbClient.connect()
    dbClient.select(sql, params)
    results = dbClient.fetchall()
    print(results)
    grouped_data = []
    for row in results:
        
      # Building/Place
      building_index = next((index for (index, d) in enumerate(grouped_data) if d['Building_code'] == row['Building_code'] and d['Place_type_code'] == row['Place_type_code']), None)
      if building_index is None:
        grouped_data.append({
          'Building_code': row['Building_code'],
          'Building_name': row['Building_name'],
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