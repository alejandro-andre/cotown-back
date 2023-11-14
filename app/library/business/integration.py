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
    SELECT DISTINCT * FROM (
      SELECT
        c.id,
        c."Type" AS "type", 
        CASE 
          WHEN r."Owner_id" = 10 THEN TRUE
          ELSE FALSE
        END AS "third_party",
        i."Name" AS "document_type",
        CASE 
          WHEN c."Id_type_id" IN (1, 2, 5) THEN 'ES'
          ELSE na."Code" 
        END AS "document_country",
        c."Document" AS "document", 
        c."Name" AS "name", 
        c."Address" AS "address", 
        c."Zip" AS "zip", 
        c."City" AS "city", 
        c."Province" AS "province", 
        co."Code" AS "country",
        c."Bank_account" AS "bank_account"
      FROM "Customer"."Customer" c
        INNER JOIN "Booking"."Booking_group" b ON b."Payer_id" = c.id
        INNER JOIN "Booking"."Booking_rooming" br ON br."Booking_id" = b.id
        LEFT JOIN "Auxiliar"."Id_type" i ON i.id = c."Id_type_id"
        LEFT JOIN "Geo"."Country" co ON co.id = c."Country_id" 
        LEFT JOIN "Geo"."Country" na ON na.id = c."Nationality_id" 
        LEFT JOIN "Resource"."Resource" r ON r.id = br."Resource_id" 
      WHERE 
        b."Status" NOT IN ('grupobloqueado') AND 
        (
          c."Created_at" >= '{date}' OR 
          c."Updated_at" >= '{date}' OR
          b."Created_at" >= '{date}' OR 
          b."Updated_at" >= '{date}'
        )
      UNION
      SELECT
        c.id,
        c."Type" AS "type", 
        CASE 
          WHEN r."Owner_id" = 10 THEN TRUE
          ELSE FALSE
        END AS "third_party",
        i."Name" AS "document_type",
        CASE 
          WHEN c."Id_type_id" IN (1, 2, 5) THEN 'ES'
          ELSE na."Code" 
        END AS "document_country",
        c."Document" AS "document", 
        c."Name" AS "name", 
        c."Address" AS "address", 
        c."Zip" AS "zip", 
        c."City" AS "city", 
        c."Province" AS "province", 
        co."Code" AS "country",
        c."Bank_account" AS "bank_account"
      FROM "Customer"."Customer" c
        INNER JOIN "Booking"."Booking" b ON b."Payer_id" = c.id
        LEFT JOIN "Auxiliar"."Id_type" i ON i.id = c."Id_type_id"
        LEFT JOIN "Geo"."Country" co ON co.id = c."Country_id" 
        LEFT JOIN "Geo"."Country" na ON na.id = c."Nationality_id" 
        LEFT JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
      WHERE 
        b."Status" NOT IN ('solicitud', 'alternativas', 'pendientepago', 'finalizada', 'descartada', 'cancelada', 'caducada') AND
        (
          c."Created_at" >= '{date}' OR 
          c."Updated_at" >= '{date}' OR
          b."Created_at" >= '{date}' OR 
          b."Updated_at" >= '{date}'
        )
    ) AS customers
    ORDER BY 1
  '''
  try:
    dbClient.connect()
    dbClient.select(sql)
    column_names = [desc[0] for desc in dbClient.sel.description]
    result = [{col: (row[i] if row[i] is not None else '') for i, col in enumerate(column_names)} for row in dbClient.fetchall()]
    dbClient.disconnect()
    return result
 
  except Exception as error:
    logger.error(error)
    dbClient.rollback()
    return None