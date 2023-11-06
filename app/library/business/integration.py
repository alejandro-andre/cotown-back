# ######################################################
# Imports
# ######################################################

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ######################################################
# Integration queries
# ######################################################

# ------------------------------------------------------
# Client query
# ------------------------------------------------------

def q_int_clients(dbClient, date):

  sql = f'''
  SELECT DISTINCT 
    id, "Type", "case" AS "Third_party", "Document", "Name", "Address", "Zip", "City", "Province", "Code" AS "Country", "Email"
  FROM (
    SELECT c.id, c."Type", 
      CASE 
        WHEN r."Owner_id" = 10 THEN TRUE
        ELSE FALSE
      END CASE, 
      c."Document", c."Name", c."Address", c."Zip", c."City", 
      COALESCE(c."Province", '') AS "Province", co."Code" , c."Email"
    FROM "Booking"."Booking_price" bp
    INNER JOIN "Booking"."Booking" b on b.id = bp."Booking_id" 
    INNER JOIN "Resource"."Resource" r on r.id = b."Resource_id" 
    INNER JOIN "Customer"."Customer" c on c.id = b."Payer_id" 
    INNER JOIN "Geo"."Country" co on co.id = c."Country_id" 
    WHERE (c."Created_at" >= '{date}' OR c."Updated_at" >= '{date}')
    UNION
    SELECT c.id, c."Type", 
      CASE 
        WHEN r."Owner_id" = 10 THEN TRUE
        ELSE FALSE
      END CASE, 
      c."Document", c."Name", c."Address", c."Zip", c."City", 
      COALESCE(c."Province", '') AS "Province", co."Code" , c."Email"
    FROM "Booking"."Booking_rooming" br
    INNER JOIN "Booking"."Booking_group" bg on bg.id = br."Booking_id" 
    INNER JOIN "Resource"."Resource" r on r.id = br."Resource_id" 
    INNER JOIN "Customer"."Customer" c on c.id = bg."Payer_id" 
    INNER JOIN "Geo"."Country" co on co.id = c."Country_id" 
    WHERE (c."Created_at" >= '{date}' OR c."Updated_at" >= '{date}')
  ) AS customers
  ORDER BY 1;
  '''
  try:
    dbClient.connect()
    dbClient.select(sql)
    result = [dict(row) for row in dbClient.fetchall()]
    dbClient.disconnect()
    return result
 
  except Exception as error:
    logger.error(error)
    dbClient.rollback()
    return None