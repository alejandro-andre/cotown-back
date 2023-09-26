# ######################################################
# Imports
# ######################################################

# System includes
import logging
import json
from datetime import datetime
from dateutil import relativedelta

# Logging
import logging
logger = logging.getLogger('COTOWN')



# ######################################################
# Booking process
# ######################################################

# Get information and prices of available typologies between dates
def available_types(dbClient, date_from, date_to, location):

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
    columns = [desc[0] for desc in dbClient.sel.description]
    result = [dict(zip(columns, row)) for row in dbClient.fetchall()]
    dbClient.disconnect()
    return result

  except Exception as error:
    logger.error(error)
    dbClient.rollback()
    return None