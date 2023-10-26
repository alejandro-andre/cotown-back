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
def typologies(dbClient):

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
    LEFT JOIN "Resource"."Resource_place_type" rpt on rpt.id = r."Place_type_id" 
    INNER JOIN "Geo"."District" d on d.id = b."District_id" 
    INNER JOIN "Geo"."Location" l on l.id = d."Location_id" 
    WHERE "Sale_type" IS NOT NULL
    AND rpt."Code" NOT LIKE 'DUI_%'
    GROUP BY 1, 2, 3, 4
    ORDER BY 1, 2, 3
    '''

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
def available_rooms(dbClient, date_from, date_to, city, room):
  
  # Rent info
  year, field = rent_info(date_from, date_to)
  type = 'I_%' if room == 'ind' else 'D\_%'

  sql = '''
    SELECT b."Code" as "Building_code", 
          rpt."Code" AS "Place_type_code", 
          rft."Code" AS "Flat_type_code", 
          b."Name" as "Building_name", 
          rpt."Name" AS "Place_type_name", 
          rft."Name" AS "Flat_type_name", 
          pd."{}" AS "Price",
          MIN(mrt.id) AS "Photo"
    FROM "Resource"."Resource" r
        INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
        INNER JOIN "Geo"."District" d ON d.id = b."District_id" 
        INNER JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id" 
        INNER JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id" 
        INNER JOIN "Billing"."Pricing_detail" pd ON (pd."Year" = %s AND pd."Building_id" = b.id AND pd."Flat_type_id" = rft.id AND pd."Place_type_id" = rpt.id)
        INNER JOIN "Marketing"."Media_resource_type" mrt ON (mrt."Building_id" = b.id AND mrt."Place_type_id" = rpt.id)
        LEFT JOIN "Booking"."Booking_detail" bd ON (bd."Resource_id" = r.id AND bd."Date_from" <= %s AND bd."Date_to" >= %s)
    WHERE bd.id IS NULL 
      AND b."Segment_id" = 1
      AND b."Building_type_id" < 3
      AND d."Location_id" = %s
      AND rpt."Code" LIKE %s
    GROUP BY 1, 2, 3, 4, 5, 6, 7
  '''.format(field)

  try:
    dbClient.connect()
    dbClient.select(sql, (year, date_to, date_from, city, type, ))
    results = dbClient.fetchall()
    print(sql, (year, date_to, date_from, city, type, ))
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
          'Flat_types': []
        })
        building_index = len(grouped_data) - 1

      # Flat type
      grouped_data[building_index]['Flat_types'].append({
        'Flat_type_code': row['Flat_type_code'],
        'Flat_type_name': row['Flat_type_name'],
        'Price': int(row['Price'])
      })

    dbClient.disconnect()
    return grouped_data
  
  except Exception as error:
    logger.error(error)
    dbClient.rollback()
    return None

# Get information and prices of available typologies between dates
def available_types(dbClient, date_from, date_to, location):

  # Rent info
  year, field = rent_info(date_from, date_to), y

  # SQL 
  sql = '''
    SELECT DISTINCT
      b."Name" AS "Building_name", 
      r."Flat_type_id", rft."Name" AS "Flat_type_name", rft."Name_en" AS "Flat_type_name_en", 
      r."Place_type_id", rpt."Name" AS "Place_type_name", rpt."Name_en" AS "Place_type_name_en",
      ROUND(pd."Services" + pr."Multiplier" * pd."{}", 0) AS "Rent"
    FROM 
      "Resource"."Resource" r
      INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
      INNER JOIN "Geo"."District" d on d.id = b."District_id"
      INNER JOIN "Billing"."Pricing_rate" pr ON r."Rate_id"  = pr.id
      INNER JOIN "Billing"."Pricing_detail" pd ON pd."Building_id" = r."Building_id" 
        AND pd."Flat_type_id" = r."Flat_type_id" 
        AND (pd."Place_type_id" = r."Place_type_id" OR pd."Place_type_id" IS NULL) 
      LEFT JOIN "Resource"."Resource_flat_type" rft ON rft.id = r."Flat_type_id"
      LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
      LEFT JOIN "Booking"."Booking_detail" bd ON bd."Resource_id" = r.id 
        AND bd."Date_from" <= %s
        AND bd."Date_to" >= %s
    WHERE b."Active"
      AND pd."Year" = %s
      AND d."Location_id" = %s
      AND bd.id IS NULL
    ORDER BY 1, 2, 3;
    '''.format(field, field)

  try:
    dbClient.connect()
    dbClient.select(sql, (date_to, date_from, year, location))
    #columns = [desc[0] for desc in dbClient.sel.description]
    #result = [dict(zip(columns, row)) for row in dbClient.fetchall()]
    result = json.dumps([dict(row) for row in dbClient.fetchall()], default=str)
    dbClient.disconnect()
    return result

  except Exception as error:
    logger.error(error)
    dbClient.rollback()
    return None