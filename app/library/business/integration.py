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

def q_int_customers(dbClient, date):

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
      UNION ALL
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
        WHEN i."Bill_type" = 'factura' THEN 'CI'
        ELSE 'CCM'
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
      AND i."Bill_type" <> 'recibo'
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