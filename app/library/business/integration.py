# ######################################################
# Imports
# ######################################################

# 
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ######################################################
# Integration queries
# ######################################################

# ------------------------------------------------------
# Client query
# ------------------------------------------------------

def q_int_customers(dbClient, date):

  sql = f'''
    SELECT DISTINCT * FROM (
      SELECT
        c.id,
        CASE WHEN r."Owner_id" = 10 THEN FALSE ELSE TRUE END AS "third_party",
        CASE WHEN c."Billing_type" IS NOT NULL THEN c."Billing_type" ELSE c."Type" END AS "type",
        CASE WHEN bi."Name" IS NOT NULL THEN bi."Name" ELSE i."Name" END AS "document_type",
        CASE WHEN c."Billing_id_type_id" IS NOT NULL THEN
          CASE WHEN c."Billing_id_type_id" IN (1, 2, 5) THEN 'ES' ELSE na."Code" END
        ELSE
          CASE WHEN c."Id_type_id" IN (1, 2, 5) THEN 'ES' ELSE na."Code" END
        END AS "document_country",
        CASE WHEN c."Billing_document" IS NOT NULL THEN c."Billing_document" ELSE c."Document" END AS "document", 
        CASE WHEN c."Billing_name" IS NOT NULL THEN c."Billing_name" ELSE c."Name" END AS "name", 
        CASE WHEN c."Billing_address" IS NOT NULL THEN c."Billing_address" ELSE c."Address" END AS "address", 
        CASE WHEN c."Billing_zip" IS NOT NULL THEN c."Billing_zip" ELSE c."Zip" END AS "zip", 
        CASE WHEN c."Billing_city" IS NOT NULL THEN c."Billing_city" ELSE c."City" END AS "city", 
        CASE WHEN c."Billing_province" IS NOT NULL THEN c."Billing_province" ELSE c."Province" END AS "province", 
        CASE WHEN bco."Code" IS NOT NULL THEN bco."Code" ELSE co."Code" END AS "country",
        c."IBAN" AS "direc_debit_bank_account",
        c."Same_account" AS "same_account",
        c."Bank_account" AS "bank_account",
        c."Swift" AS "swift",
        c."Bank_holder" AS "bank_holder",
        c."Bank_name" AS "bank_name",
        c."Bank_address" AS "bank_address",
        c."Bank_city" AS "bank_city",
        cc."Code" AS "bank_country"
      FROM "Customer"."Customer" c
        INNER JOIN "Booking"."Booking_group" b ON b."Payer_id" = c.id
        INNER JOIN "Booking"."Booking_group_rooming" br ON br."Booking_id" = b.id
        LEFT JOIN "Auxiliar"."Id_type" i ON i.id = c."Id_type_id"
        LEFT JOIN "Auxiliar"."Id_type" bi ON bi.id = c."Billing_id_type_id"
        LEFT JOIN "Geo"."Country" co ON co.id = c."Country_id" 
        LEFT JOIN "Geo"."Country" bco ON bco.id = c."Billing_country_id" 
        LEFT JOIN "Geo"."Country" na ON na.id = c."Nationality_id" 
        LEFT JOIN "Geo"."Country" cc ON cc.id = c."Bank_country_id" 
        LEFT JOIN "Resource"."Resource" r ON r.id = br."Resource_id" 
      WHERE 
          c."Created_at" >= '{date}' OR 
          c."Updated_at" >= '{date}' OR
          b."Created_at" >= '{date}' OR 
          b."Updated_at" >= '{date}'
      UNION ALL
      SELECT
        c.id,
        CASE WHEN r."Owner_id" = 10 THEN FALSE ELSE TRUE END AS "third_party",
        CASE WHEN c."Billing_type" IS NOT NULL THEN c."Billing_type" ELSE c."Type" END AS "type",
        CASE WHEN bi."Name" IS NOT NULL THEN bi."Name" ELSE i."Name" END AS "document_type",
        CASE WHEN c."Billing_id_type_id" IS NOT NULL THEN
          CASE WHEN c."Billing_id_type_id" IN (1, 2, 5) THEN 'ES' ELSE na."Code" END
        ELSE
          CASE WHEN c."Id_type_id" IN (1, 2, 5) THEN 'ES' ELSE na."Code" END
        END AS "document_country",
        CASE WHEN c."Billing_document" IS NOT NULL THEN c."Billing_document" ELSE c."Document" END AS "document", 
        CASE WHEN c."Billing_name" IS NOT NULL THEN c."Billing_name" ELSE c."Name" END AS "name", 
        CASE WHEN c."Billing_address" IS NOT NULL THEN c."Billing_address" ELSE c."Address" END AS "address", 
        CASE WHEN c."Billing_zip" IS NOT NULL THEN c."Billing_zip" ELSE c."Zip" END AS "zip", 
        CASE WHEN c."Billing_city" IS NOT NULL THEN c."Billing_city" ELSE c."City" END AS "city", 
        CASE WHEN c."Billing_province" IS NOT NULL THEN c."Billing_province" ELSE c."Province" END AS "province", 
        CASE WHEN bco."Code" IS NOT NULL THEN bco."Code" ELSE co."Code" END AS "country",
        c."IBAN" AS "direc_debit_bank_account",
        c."Same_account" AS "same_account",
        c."Bank_account" AS "bank_account",
        c."Swift" AS "swift",
        c."Bank_holder" AS "bank_holder",
        c."Bank_name" AS "bank_name",
        c."Bank_address" AS "bank_address",
        c."Bank_city" AS "bank_city",
        cc."Code" AS "bank_country"
      FROM "Customer"."Customer" c
        INNER JOIN "Booking"."Booking" b ON b."Customer_id" = c.id
        LEFT JOIN "Auxiliar"."Id_type" i ON i.id = c."Id_type_id"
        LEFT JOIN "Auxiliar"."Id_type" bi ON bi.id = c."Billing_id_type_id"
        LEFT JOIN "Geo"."Country" co ON co.id = c."Country_id" 
        LEFT JOIN "Geo"."Country" bco ON bco.id = c."Billing_country_id" 
        LEFT JOIN "Geo"."Country" na ON na.id = c."Nationality_id" 
        LEFT JOIN "Geo"."Country" cc ON cc.id = c."Bank_country_id" 
        LEFT JOIN "Resource"."Resource" r ON r.id = b."Resource_id" 
      WHERE 
        b."Status" NOT IN ('solicitud', 'alternativas', 'pendientepago', 'finalizada', 'descartada', 'cancelada', 'caducada')  AND
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
    con = dbClient.getconn()
    cur = dbClient.execute(con, sql)
    column_names = [desc[0] for desc in cur.description]
    result = [{col: (row[i] if row[i] is not None else '') for i, col in enumerate(column_names)} for row in cur.fetchall()]
    cur.close()
    dbClient.putconn(con)
    return result
 
  except Exception as error:
    logger.error(error)
    con.rollback()
    return None
  
# ------------------------------------------------------
# Invoices query
# ------------------------------------------------------

def q_int_invoices(dbClient, date):

  sql = f'''
    SELECT
      CASE 
        WHEN i."Provider_id" = 1 OR i."Provider_id" = 10 THEN
          CASE
	        WHEN pr."Product_type_id" = 2 THEN 'GF'
            WHEN i."Bill_type" = 'rectificativa' THEN 'CCM'
            ELSE 'CI'
          END
        ELSE
          CASE
	        WHEN pr."Product_type_id" = 2 THEN 'GF'
            WHEN i."Bill_type" = 'rectificativa' THEN 'AT'
            ELSE 'FT'
          END
      END AS "document_type",
      p."SAP_code" AS "issuer_id",
      i."Code" AS "invoice_id",
      c.id AS "customer_id",
      'EUR' AS "currency",
      TO_CHAR(i."Issued_date", 'DD/MM/YYYY') AS "date",
      i."Comments" AS "comments",
      pr."SAP_code" AS "service_id",
      il."Concept" AS "description",
      SUBSTRING(p."SAP_code", 1, 2) || r."SAP_code" AS "project_id",
      il."Amount" AS "amount",
      t."SAP_code" AS "tax_id", 
      il."Comments" AS "comments"
    FROM "Billing"."Invoice_line" il
    INNER JOIN "Billing"."Invoice" i ON i.id = il."Invoice_id"
    INNER JOIN "Billing"."Product" pr ON pr.id = il."Product_id"
    INNER JOIN "Billing"."Tax" t ON t.id = il."Tax_id" 
    INNER JOIN "Provider"."Provider" p ON p.id = i."Provider_id"
    INNER JOIN "Customer"."Customer" c ON c.id = i."Customer_id"
    INNER JOIN "Resource"."Resource" r ON r.id = il."Resource_id" 
    WHERE i."Issued"
      AND p."SAP_code" IS NOT NULL
      AND i."Issued_date" >= '{date}'
    ORDER BY 2, 3
  '''
  try:
    con = dbClient.getconn()
    cur = dbClient.execute(con, sql)
    result = []
    for row in cur.fetchall():
      invoice_index = next((index for (index, d) in enumerate(result) if d['issuer_id'] == row['issuer_id'] and d['invoice_id'] == row['invoice_id']), None)
      if invoice_index is None:
        result.append({
          'comments': row['comments'],
          'currency': row['currency'],
          'customer_id': row['customer_id'],
          'date': row['date'],
          'document_type': row['document_type'],
          'invoice_id': row['invoice_id'],
          'issuer_id': row['issuer_id'],
          'lines': []
        })
        invoice_index = len(result) - 1
      result[invoice_index]['lines'].append({
        'amount': row['amount'],
        'comments': row['comments'],
        'description': row['description'],
        'project_id': row['project_id'],
        'service_id': row['service_id'],
        'tax_id': row['tax_id']
      })
    cur.close()
    dbClient.putconn(con)
    return result
 
  except Exception as error:
    logger.error(error)
    con.rollback()
    return None
  

# ------------------------------------------------------
# Management fees query
# ------------------------------------------------------

def q_int_management_fees(dbClient, fdesde):

  # Next month
  fhasta = datetime.strftime(datetime.strptime(fdesde, '%Y-%m-%d') + relativedelta(months=1), '%Y-%m-%d')

  # Query
  sql = f'''
    SELECT 
      "month", "owner", "resource", 
      round(sum("gross"), 2) AS "gross",
      round(sum("net"), 2) AS "net",
      round(sum("fee"), 2) AS "fee"
    FROM (
      SELECT TO_CHAR(i."Issued_date", 'YYYY-MM') AS "month", 
        p."SAP_code" as "owner",
        bu."Code" AS "resource",
        il."Amount" AS "gross",
        il."Amount" / (1 + t."Value" / 100) AS "net",
        il."Amount" / (1 + t."Value" / 100) * r."Management_fee" / 100 AS "fee"
      FROM "Billing"."Invoice_line" il
        INNER JOIN "Billing"."Tax" t ON t.id = il."Tax_id"
        INNER JOIN "Billing"."Invoice" i on i.id = il."Invoice_id"  
        INNER JOIN "Provider"."Provider" p on p.id = i."Provider_id" 
        LEFT JOIN "Booking"."Booking" b on b.id = i."Booking_id" 
        LEFT JOIN "Resource"."Resource" r on r.id = b."Resource_id"
        LEFT JOIN "Building"."Building" bu on bu.id = r."Building_id"
      WHERE i."Issued" AND p.id <> 1 AND i."Booking_group_id" IS NULL 
        AND i."Issued_date" >= '{fdesde}' AND i."Issued_date" < '{fhasta}'
      UNION ALL
      SELECT TO_CHAR(i."Issued_date", 'YYYY-MM') AS "month",
        p."SAP_code" as "owner", 
        bu."Code" AS "resource",
        il."Amount" AS "gross",
        il."Amount" / (1 + t."Value" / 100) AS "net",
        il."Amount" / (1 + t."Value" / 100) * r."Management_fee" / 100 AS "fee"
      FROM "Billing"."Invoice_line" il
        INNER JOIN "Billing"."Tax" t ON t.id = il."Tax_id"
        INNER JOIN "Billing"."Invoice" i on i.id = il."Invoice_id"  
        INNER JOIN "Provider"."Provider" p on p.id = i."Provider_id" 
        LEFT JOIN "Booking"."Booking_group" b on b.id = i."Booking_group_id" 
        LEFT JOIN "Resource"."Resource" r on r.id = il."Resource_id"
        LEFT JOIN "Building"."Building" bu on bu.id = b."Building_id"  
      WHERE i."Issued" AND p.id <> 1 AND i."Booking_id" IS NULL 
        AND i."Issued_date" >= '{fdesde}' AND i."Issued_date" < '{fhasta}'
    ) AS "data"
    GROUP BY 1, 2, 3
  '''
  try:
    con = dbClient.getconn()
    cur = dbClient.execute(con, sql)
    column_names = [desc[0] for desc in cur.description]
    result = [{col: (row[i] if row[i] is not None else '') for i, col in enumerate(column_names)} for row in cur.fetchall()]
    cur.close()
    dbClient.putconn(con)
    return result
 
  except Exception as error:
    logger.error(error)
    con.rollback()
    return None  