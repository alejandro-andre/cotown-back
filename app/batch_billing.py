# ###################################################
# Batch process
# ---------------------------------------------------
# Billing process
# ###################################################

# ###################################################
# Imports
# ###################################################

# System includes
from datetime import datetime

# Cotown includes
from library.services.config import settings
from library.services.dbclient import DBClient

# Logging
import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger('COTOWN')


# ###################################################
# Constants
# ###################################################

ID_COTOWN = 1

PM_CARD = 1
PM_TRANSFER = 2

PR_BOOKING_FEE = 1
PR_DEPOSIT = 2
PR_RENT = 3
PR_SERVICES = 4
PR_CHECKIN = 10

VAT_21 = 1
VAT_0  = 2

PRODUCTS = {}

# ###################################################
# Get structure data
# ###################################################

def get_data(dbClient, con):

  # Capture exceptions
  try:

    # Get product list
    con = dbClient.getconn()
    cur = dbClient.execute(con, 
      '''
      SELECT p.id, p."Name", p."Name_en", t.id, t."Name", t."Name_en", t."Value"
      FROM "Billing"."Product" p
      INNER JOIN "Billing"."Tax" t ON t.id = p."Tax_id";
      ''')
    data = cur.fetchall()
    cur.close()
    for product in data:
      PRODUCTS[product[0]] = {
        'id': product[0],
        'concept': product[1],
        'tax': product[3],
        'value': product[5]
      }

  except Exception as error:
    logger.error(error)
    con.rollback()


# ###################################################
# Generate membership fee and deposit payment bills
# ###################################################

def bill_payments(dbClient, con):

  # Get all payments without bill
  cur = dbClient.execute(con, 
    '''
    SELECT p.id, p."Payment_type", p."Customer_id", p."Booking_id", p."Payment_method_id", p."Amount", r."Owner_id", r."Code", pr."Receipt"
    FROM "Billing"."Payment" p
    INNER JOIN "Booking"."Booking" b ON p."Booking_id" = b.id
    INNER JOIN "Resource"."Resource" r ON b."Resource_id" = r.id
    INNER JOIN "Provider"."Provider" pr ON pr.id = r."Owner_id"
    LEFT JOIN "Billing"."Invoice" i ON i."Payment_id" = p.id
    WHERE i.id IS NULL
    AND ("Payment_date" IS NOT NULL OR "Payment_type" = 'checkin')
    ORDER BY p."Booking_id"
    ''')
  data = cur.fetchall()
  cur.close()

  # Loop thru payments
  num = 0
  err = 0
  for item in data:

    # Debug
    logger.debug(item)

    # Capture exceptions
    try:

      # Product id
      pid = PR_SERVICES
      if item['Payment_type'] == 'booking':
        pid = PR_BOOKING_FEE
      if item['Payment_type'] == 'deposito':
        pid = PR_DEPOSIT
      if item['Payment_type'] == 'checkin':
        pid = PR_CHECKIN

      # Create invoice
      cur = dbClient.execute(con, 
        '''
        INSERT INTO "Billing"."Invoice"
        ("Bill_type", "Issued", "Rectified", "Issued_date", "Provider_id", "Customer_id", "Booking_id", "Payment_method_id", "Payment_id", "Concept")
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        ''',
        (
          'recibo' if item['Payment_type'] not in ('booking','checkin') and (item['Payment_type'] == 'deposito' or item['Receipt']) else 'factura',
          False,
          False,
          datetime.now(),
          ID_COTOWN if item['Payment_type'] in ('booking','checkin') else item['Owner_id'],
          item['Customer_id'],
          item['Booking_id'],
          item['Payment_method_id'],
          item['id'],
          PRODUCTS[pid]['concept'],
        )
      )
      billid = cur.fetchone()[0]

      # Create invoice line
      cur = dbClient.execute(con, 
        '''
        INSERT INTO "Billing"."Invoice_line"
        ("Invoice_id", "Amount", "Product_id", "Tax_id", "Concept")
        VALUES (%s, %s, %s, %s, %s)
        ''',
        (
          billid,
          item['Amount'],
          pid,
          PRODUCTS[pid]['tax'],
          PRODUCTS[pid]['concept'] + ' ' + item['Code']
        )
      )

      # Update invoice
      cur = dbClient.execute(con, 'UPDATE "Billing"."Invoice" SET "Issued" = %s WHERE id = %s', (True, billid))
      con.commit()
      num += 1

    # Process exception
    except Exception as error:
      err += 1
      logger.error(error)
      con.rollback()

  # End
  logger.info('{} payment invoices generated'.format(num))
  if err > 0:
    logger.error('{} payment invoices not ok'.format(err))
  else:    
    logger.info('{} payment invoices ok'.format(err))
  return

# ###################################################
# Generate monthly bills
# ###################################################

def bill_month(dbClient, con):

  # Get all prices not already billed
  cur = dbClient.execute(con,
    '''
    SELECT 
      p.id, p."Booking_id", p."Rent", p."Services", p."Rent_discount", p."Services_discount", p."Rent_date", p."Invoice_external",
      b."Customer_id", b."Tax_id" as "Tax", c."Payment_method_id", r.id as "Resource_id", r."Code", r."Owner_id", r."Service_id", st."Tax_id", pr."Receipt", 
      pr."Pos" as "Rent_pos", sv."Pos" as "Service_pos"
    FROM "Booking"."Booking_price" p
      INNER JOIN "Booking"."Booking" b ON p."Booking_id" = b.id
      INNER JOIN "Customer"."Customer" c ON b."Customer_id" = c.id
      INNER JOIN "Resource"."Resource" r ON b."Resource_id" = r.id
      INNER JOIN "Provider"."Provider" pr ON pr.id = r."Owner_id"
      LEFT JOIN "Provider"."Provider" sv ON sv.id = r."Service_id"
      INNER JOIN "Building"."Building" bu ON bu.id = r."Building_id"
      INNER JOIN "Building"."Building_type" st ON st.id = bu."Building_type_id"
    WHERE b."Status" IN ('firmacontrato', 'checkinconfirmado', 'contrato','checkin', 'inhouse', 'checkout', 'revision')
      AND "Invoice_rent_id" IS NULL
      AND "Invoice_services_id" IS NULL
      AND "Rent_date" <= CURRENT_DATE
      AND "Rent_date" >= %s
    ''', (settings.BILLDATE, ))
  data = cur.fetchall()
  cur.close()

  # Loop thru monthly prices
  num = 0
  err = 0
  for item in data:

    # Capture exceptions
    try:

      # Payment method for external invoices
      if item['Invoice_external']:
        item['Payment_method_id'] = 5

      # Get all asap and recurrent extra rent
      cur = dbClient.execute(con,
        '''
        SELECT s.id, s."Concept", s."Amount", s."Tax_id", s."Product_id", s."Provider_id", s."Extra_type", p."Product_type_id"
        FROM "Booking"."Booking_service" s
          INNER JOIN "Billing"."Product" p ON p.id = s."Product_id"
        WHERE s."Booking_id" = %s
          AND p."Product_type_id" = 3
          AND (
            (s."Extra_type" = 'asap' AND s."Invoice_services_id" IS NULL)
            OR 
            (s."Billing_date_to" >= CURRENT_DATE AND s."Billing_date_from" <= CURRENT_DATE)
          )
        ''', (item['Booking_id'], ))
      extra_rent = cur.fetchall()
      cur.close()
      total_extra_rent = float(sum(r['Amount'] for r in extra_rent) or 0.0)

      # Get all recurrent extra services
      cur = dbClient.execute(con,
        '''
        SELECT s.id, s."Concept", s."Amount", s."Tax_id", s."Product_id", s."Provider_id", s."Extra_type", p."Product_type_id"
        FROM "Booking"."Booking_service" s
          INNER JOIN "Billing"."Product" p ON p.id = s."Product_id"
        WHERE s."Booking_id" = %s
          AND p."Product_type_id" <> 3
          AND (
            (s."Extra_type" = 'asap' AND s."Invoice_services_id" IS NULL)
            OR 
            (s."Billing_date_to" >= CURRENT_DATE AND s."Billing_date_from" <= CURRENT_DATE)
          )
        ''', (item['Booking_id'], ))
      extra_services = cur.fetchall()
      cur.close()
      total_extra_services = float(sum(r['Amount'] for r in extra_services) or 0.0)

      # Amounts
      total_rent = float(item['Rent'] or 0.0) + float(item['Rent_discount'] or 0.0)
      total_services = float(item['Services'] or 0.0) + float(item['Services_discount'] or 0.0)
      if total_rent + total_services != 0:
        logger.debug(item)

      # Same issuer
      product = PRODUCTS[PR_RENT]
      if item['Owner_id'] == item['Service_id']:
        total_rent = total_rent + total_services
        total_extra_rent = total_extra_rent + total_extra_services
        extra_rent = extra_rent + extra_services
        total_services = 0
        total_extra_services = 0
        extra_services = []
      if total_services > 0:
        if item['Rent_pos'] != item['Service_pos']:
          item['Rent_pos'] = 'delegado'
       
      # Create payment
      if total_rent + total_services + total_extra_rent + total_extra_services > 0:

        cur = dbClient.execute(con,
          '''
          INSERT INTO "Billing"."Payment"
          ("Payment_method_id", "Pos", "Customer_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" )
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
          RETURNING id
          ''',
          (
            item['Payment_method_id'] if item['Payment_method_id'] is not None else PM_CARD,
            item['Rent_pos'],
            item['Customer_id'],
            item['Booking_id'],
            total_rent + total_services + total_extra_rent + total_extra_services,
            datetime.now(),
            product['concept'] + ' [' + item['Code'] + '] ' + str(item['Rent_date']),
            'servicios'
          )
        )
        paymentid = cur.fetchone()[0]

        # Create rent invoice
        if total_rent + total_extra_rent > 0:

          cur = dbClient.execute(con, 
          '''
            INSERT INTO "Billing"."Invoice"
            ("Bill_type", "Issued", "Rectified", "Issued_date", "Provider_id", "Customer_id", "Booking_id", "Payment_method_id", "Payment_id", "Concept")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            ''',
            (
              'recibo' if item['Receipt'] else 'factura',
              False,
              False,
              datetime.now(),
              item['Owner_id'],
              item['Customer_id'],
              item['Booking_id'],
              item['Payment_method_id'] if item['Payment_method_id'] is not None else PM_CARD,
              paymentid,
              product['concept'] + ' [' + item['Code'] + '] ' + str(item['Rent_date'])[:7]
            )
          )
          rentid = cur.fetchone()[0]

          # Monthly rent
          dbClient.execute(con, 
            '''
            INSERT INTO "Billing"."Invoice_line"
            ("Invoice_id", "Resource_id", "Amount", "Product_id", "Tax_id", "Concept")
            VALUES (%s, %s, %s, %s, %s, %s)
            ''',
            (
              rentid,
              item['Resource_id'],
              total_rent,
              PR_RENT,
              item['Tax'] if item['Tax'] is not None else item['Tax_id'] if item['Tax_id'] is not None else VAT_0,
              product['concept'] + ' [' + item['Code'] + '] ' + str(item['Rent_date'])[:7]
            )
          )

          # Extra rent
          if total_extra_rent > 0:
            for e in extra_rent:
              dbClient.execute(con,
                '''
                INSERT INTO "Billing"."Invoice_line"
                ("Invoice_id", "Resource_id", "Amount", "Product_id", "Tax_id", "Concept")
                VALUES (%s, %s, %s, %s, %s, %s)
                ''',
                ( rentid,
                  item['Resource_id'],
                  e['Amount'],
                  e['Product_id'],
                  e['Tax_id'],
                  e['Concept']
                )
              )

          # Update invoice
          dbClient.execute(con, 'UPDATE "Billing"."Invoice" SET "Issued" = %s WHERE id = %s', (True, rentid))

          # Update extra rent
          for e in extra_rent:
            dbClient.execute(con, 'UPDATE "Booking"."Booking_service" SET "Invoice_services_id" = %s WHERE id = %s', (rentid, e['id']))

          # Update price
          dbClient.execute(con, 'UPDATE "Booking"."Booking_price" SET "Invoice_rent_id" = %s WHERE id = %s', (rentid, item['id']))
          q = 1

        # Create services invoice
        if total_services + total_extra_services > 0:
         
          cur = dbClient.execute(con,
            '''
            INSERT INTO "Billing"."Invoice"
            ("Bill_type", "Issued", "Rectified", "Issued_date", "Provider_id", "Customer_id", "Booking_id", "Payment_method_id", "Payment_id", "Concept")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            ''',
            (
              'factura',
              False,
              False,
              datetime.now(),
              item['Service_id'],
              item['Customer_id'],
              item['Booking_id'],
              item['Payment_method_id'] if item['Payment_method_id'] is not None else PM_CARD,
              paymentid,
              PRODUCTS[PR_SERVICES]['concept'] + ' [' + item['Code'] + '] ' + str(item['Rent_date'])[:7]
            )
          )
          servid = cur.fetchone()[0]

          # Monthly services
          if total_services > 0:
            dbClient.execute(con,
              '''
              INSERT INTO "Billing"."Invoice_line"
              ("Invoice_id", "Resource_id", "Amount", "Product_id", "Tax_id", "Concept")
              VALUES (%s, %s, %s, %s, %s, %s)
              ''',
              (
                servid,
                item['Resource_id'],
                total_services,
                PR_SERVICES,
                PRODUCTS[PR_SERVICES]['tax'] if item['Tax_id'] is None else item['Tax_id'],
                PRODUCTS[PR_SERVICES]['concept'] + ' [' + item['Code'] + '] ' + str(item['Rent_date'])[:7]
              )
            )

          # Extra services
          if total_extra_services > 0:
            for e in extra_services:
              dbClient.execute(con,
                '''
                INSERT INTO "Billing"."Invoice_line"
                ("Invoice_id", "Resource_id", "Amount", "Product_id", "Tax_id", "Concept")
                VALUES (%s, %s, %s, %s, %s, %s)
                ''',
                ( servid,
                  item['Resource_id'],
                  e['Amount'],
                  e['Product_id'],
                  e['Tax_id'],
                  e['Concept']
                )
              )

          # Update invoice
          dbClient.execute(con, 'UPDATE "Billing"."Invoice" SET "Issued" = %s WHERE id = %s', (True, servid))

          # Update extra services
          for e in extra_services:
            dbClient.execute(con, 'UPDATE "Booking"."Booking_service" SET "Invoice_services_id" = %s WHERE id = %s', (servid, e['id']))

          # Update price
          dbClient.execute(con, 'UPDATE "Booking"."Booking_price" SET "Invoice_services_id" = %s WHERE id = %s', (servid, item['id']))
          q = 2

        # Commit
        con.commit()
        num += q

    # Process exception
    except Exception as error:
      err += 1
      logger.error(error)
      con.rollback()

  # End
  logger.info('{} rent invoices generated'.format(num))
  if err > 0:
    logger.error('{} rent invoices not ok'.format(err))
  else:
    logger.info('{} rent invoices ok'.format(err))
  return


# ###################################################
# Generate monthly bills for group bookings
# ###################################################

def bill_group_month(dbClient, con):

  # Get all prices not already billed
  cur = dbClient.execute(con,
  '''
  SELECT 
    bgp.id, bgp."Booking_id", bgp."Rent_date", bgp."Rent", bgp."Services", bg."Payer_id", bg."Tax", pr."Receipt", st."Tax_id",
    pr."Pos" as "Rent_pos", sv."Pos" as "Service_pos",
    COUNT(r."Code") as num, 
    MIN(bg."Room_ids") as "Room_ids", 
    MIN(r."Owner_id") as "Owner_id", 
    MIN(r."Service_id") as "Service_id"
  FROM "Booking"."Booking_group_price" bgp
    INNER JOIN "Booking"."Booking_group" bg ON bg.id = bgp."Booking_id"
    INNER JOIN "Booking"."Booking_group_rooms" br ON bg.id = br."Booking_id"
    INNER JOIN "Resource"."Resource" r ON r.id = br."Resource_id"
    INNER JOIN "Provider"."Provider" pr ON pr.id = r."Owner_id"
    LEFT JOIN "Provider"."Provider" sv ON sv.id = r."Service_id"
    INNER JOIN "Building"."Building" bu ON bu.id = bg."Building_id"
    INNER JOIN "Building"."Building_type" st ON st.id = bu."Building_type_id"
  WHERE bg."Status" IN ('grupoconfirmado','inhouse')
    AND bgp."Invoice_rent_id" IS NULL
    AND bgp."Rent_date" <= CURRENT_DATE
    AND bgp."Rent_date" >= %s
  GROUP BY bgp.id, bgp."Booking_id", bgp."Rent_date", bgp."Rent", bgp."Services", bg."Payer_id", bg."Tax", pr."Receipt", st."Tax_id", pr."Pos", sv."Pos"
  ORDER BY bgp."Booking_id", bgp."Rent_date"
  ''', (settings.BILLDATE, ))
  data = cur.fetchall()
  cur.close()

  # Loop thru monthly prices
  num = 0
  err = 0
  for item in data:

    # Capture exceptions
    try:

      # Group rooming list by flat
      flats = {}
      for r in item['Room_ids']:
        key = r[:12]
        if key not in flats:
          flats[key] = []
        flats[key].append(r[13:])

      # Get all flat ids
      args = tuple(flats.keys())
      cur = dbClient.execute(con, 'SELECT r."Code", id FROM "Resource"."Resource" r WHERE r."Code" IN %s ORDER BY r."Code"', (args, ))
      flat_ids = cur.fetchall()
      cur.close()

      # Get all recurrent extra rent
      cur = dbClient.execute(con,
        '''
        SELECT s."Concept", s."Amount", s."Tax_id", s."Product_id", s."Provider_id", p."Product_type_id"
        FROM "Booking"."Booking_group_service" s
          INNER JOIN "Billing"."Product" p ON p.id = s."Product_id"
        WHERE s."Booking_id" = %s
          AND s."Billing_date_to" >= CURRENT_DATE
          AND s."Billing_date_from" <= CURRENT_DATE 
          AND p."Product_type_id" = 3
        ''', (item['Booking_id'], ))
      extra_rent = cur.fetchall()
      cur.close()
      total_extra_rent = float(sum(r['Amount'] for r in extra_rent) or 0.0)

      # Get all recurrent extra services
      cur = dbClient.execute(con,
        '''
        SELECT s."Concept", s."Amount", s."Tax_id", s."Product_id", s."Provider_id", p."Product_type_id"
        FROM "Booking"."Booking_group_service" s
          INNER JOIN "Billing"."Product" p ON p.id = s."Product_id"
        WHERE s."Booking_id" = %s
          AND s."Billing_date_to" >= CURRENT_DATE
          AND s."Billing_date_from" <= CURRENT_DATE 
        ''', (item['Booking_id'], ))
      extra_services = cur.fetchall()
      cur.close()
      total_extra_services = float(sum(r['Amount'] for r in extra_services) or 0.0)

      # Amounts
      total_rent = float(item['Rent'] or 0.0) * float(item['num'] or 0.0)
      total_services = float(item['Services'] or 0.0) * float(item['num'] or 0.0)
      if total_rent + total_services != 0:
        logger.debug(item)

      # Same issuer
      product = PRODUCTS[PR_RENT]
      if item['Owner_id'] == item['Service_id']:
        total_rent = total_rent + total_services
        total_extra_rent = total_extra_rent + total_extra_services
        extra_rent = extra_rent + extra_services
        total_services = 0
        total_extra_services = 0
        extra_services = 0
      if total_services > 0:
        if item['Rent_pos'] != item['Service_pos']:
          item['Rent_pos'] = 'delegado'
          
      # Create payment
      if total_rent + total_services + total_extra_rent + total_extra_services > 0:

        cur = dbClient.execute(con,
          '''
          INSERT INTO "Billing"."Payment"
          ("Payment_method_id", "Pos", "Customer_id", "Booking_group_id", "Amount", "Issued_date", "Concept", "Payment_type" )
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
          RETURNING id
          ''',
          (
            PM_TRANSFER,
            item['Rent_pos'],
            item['Payer_id'],
            item['Booking_id'],
            total_rent + total_services + total_extra_services,
            datetime.now(),
            product['concept'] + ' (' + str(item['num']) + ' plazas) ' + str(item['Rent_date'])[:7],
            'servicios'
          )
        )
        paymentid = cur.fetchone()[0]

        # Create rent invoice
        if total_rent > 0:

          cur = dbClient.execute(con,
            '''
            INSERT INTO "Billing"."Invoice"
            ("Bill_type", "Issued", "Rectified", "Issued_date", "Provider_id", "Customer_id", "Booking_group_id", "Payment_method_id", "Payment_id", "Concept", "Comments")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            ''',
            (
              'recibo' if item['Receipt'] else 'factura',
              False,
              False,
              datetime.now(),
              item['Owner_id'],
              item['Payer_id'],
              item['Booking_id'],
              PM_TRANSFER,
              paymentid,
              product['concept'] + ' (' + str(item['num']) + ' plazas) ' + str(item['Rent_date'])[:7],
              ''
            )
          )
          rentid = cur.fetchone()[0]

          # Monthly rent
          for flat in flat_ids:
            places = len(flats[flat[0]])
            if item['Owner_id'] == item['Service_id']:
              rent = places * (float(item['Rent'] or 0.0) + float(item['Services'] or 0.0))
            else:
              rent = places * float(item['Rent'] or 0.0)
            dbClient.execute(con,
              '''
              INSERT INTO "Billing"."Invoice_line"
              ("Invoice_id", "Resource_id", "Amount", "Product_id", "Tax_id", "Concept", "Comments")
              VALUES (%s, %s, %s, %s, %s, %s, %s)
              ''',
              (
                rentid,
                flat[1],
                rent,
                product['id'],               
                (VAT_0 if item['Tax'] else VAT_21) if item['Tax_id'] is None else item['Tax_id'],
                product['concept'] + ' (' + str(places) + ' plazas) ' + str(item['Rent_date'])[:7],
                'Plazas: ' + flat[0] + ' ' + (', '.join(flats[flat[0]]))
              )
            )

            # Extra rent
            if total_extra_rent > 0:
              for e in extra_rent:
                rent = places * float(e['Amount'] or 0.0)
                dbClient.execute(con,
                  '''
                  INSERT INTO "Billing"."Invoice_line"
                  ("Invoice_id", "Resource_id", "Amount", "Product_id", "Tax_id", "Concept")
                  VALUES (%s, %s, %s, %s, %s, %s)
                  ''',
                  ( rentid,
                    flat[1],
                    rent,
                    e['Product_id'],
                    e['Tax_id'],
                    e['Concept']
                  )
                )

          # Update invoice
          dbClient.execute(con, 'UPDATE "Billing"."Invoice" SET "Issued" = %s WHERE id = %s', (True, rentid))

          # Update price
          dbClient.execute(con, 'UPDATE "Booking"."Booking_group_price" SET "Invoice_rent_id" = %s WHERE id = %s', (rentid, item['id']))
          q = 1

        # Create services invoice
        if total_services + total_extra_services > 0:
         
          cur = dbClient.execute(con,
            '''
            INSERT INTO "Billing"."Invoice"
            ("Bill_type", "Issued", "Rectified", "Issued_date", "Provider_id", "Customer_id", "Booking_group_id", "Payment_method_id", "Payment_id", "Concept", "Comments")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            ''',
            (
              'factura',
              False,
              False,
              datetime.now(),
              item['Service_id'],
              item['Payer_id'],
              item['Booking_id'],
              PM_TRANSFER,
              paymentid,
              PRODUCTS[PR_SERVICES]['concept'] + ' (' + str(item['num']) + ' plazas) ' + str(item['Rent_date'])[:7],
              ''
            )
          )
          servid = cur.fetchone()[0]

          # Monthly services
          for flat in flat_ids:
            places = len(flats[flat[0]])
            services = places * float(item['Services'] or 0.0)
            dbClient.execute(con,
              '''
              INSERT INTO "Billing"."Invoice_line"
              ("Invoice_id", "Resource_id", "Amount", "Product_id", "Tax_id", "Concept", "Comments")
              VALUES (%s, %s, %s, %s, %s, %s, %s)
              ''',
              (
                servid,
                flat[1],
                services, 
                PR_SERVICES,
                PRODUCTS[PR_SERVICES]['tax'], 
                PRODUCTS[PR_SERVICES]['concept'] + ' (' + str(places) + ' plazas) ' + str(item['Rent_date'])[:7], 
                'Plazas: ' + flat[0] + ' ' + (', '.join(flats[flat[0]]))
              )
            )

            # Extra services
            if total_extra_services > 0:
              for e in extra_services:
                services = places * float(e['Amount'] or 0.0)
                dbClient.execute(con,
                  '''
                  INSERT INTO "Billing"."Invoice_line"
                  ("Invoice_id", "Resource_id", "Amount", "Product_id", "Tax_id", "Concept")
                  VALUES (%s, %s, %s, %s, %s, %s)
                  ''',
                  ( servid,
                    flat[1],
                    services,
                    e['Product_id'],
                    e['Tax_id'],
                    e['Concept']
                  )
                )

          # Update invoice
          dbClient.execute(con, 'UPDATE "Billing"."Invoice" SET "Issued" = %s WHERE id = %s', (True, servid))

          # Update price
          dbClient.execute(con, 'UPDATE "Booking"."Booking_group_price" SET "Invoice_services_id" = %s WHERE id = %s', (servid, item['id']))
          q = 2

        # Commit
        con.commit()
        num += q
           
    # Process exception
    except Exception as error:
      err += 1
      logger.error(error)
      con.rollback()

  # End
  logger.info('{} rent group invoices generated'.format(num))
  if err > 0: 
    logger.error('{} rent group invoices not ok'.format(err))
  else: 
    logger.info('{} rent group invoices ok'.format(err))
  return


# ###################################################
# Generate service bills
# ###################################################

def bill_concepts(dbClient, con):

  # Get all non recurrent services not already billed
  cur = dbClient.execute(con,
    '''
    SELECT
      s.id, b.id as "Booking_id", b."Customer_id",
      s."Concept", s."Comments", s."Amount", s."Tax_id", s."Product_id", s."Payment_method_id", s."Provider_id",
      p."Product_type_id",
      r."Code", r."Owner_id", r."Service_id",
      pr."Pos",pr ."Receipt"
    FROM "Booking"."Booking" b
      INNER JOIN "Booking"."Booking_service" s ON s."Booking_id" = b.id
      INNER JOIN "Customer"."Customer" c ON b."Customer_id" = c.id
      INNER JOIN "Resource"."Resource" r ON b."Resource_id" = r.id
      INNER JOIN "Billing"."Product" p ON p.id = s."Product_id"
      INNER JOIN "Provider"."Provider" pr ON pr.id = s."Provider_id"
    WHERE b."Status" IN ('firmacontrato', 'checkinconfirmado', 'contrato', 'checkin', 'inhouse', 'checkout', 'revision', 'finalizada')
      AND b."Date_from" <= CURRENT_DATE
      AND s."Invoice_services_id" IS NULL
      AND s."Extra_type" = 'puntual'
      AND s."Billing_date_to" IS NULL
      AND s."Billing_date_from" <= CURRENT_DATE 
    ''')
  data = cur.fetchall()
  cur.close()

  # Loop thru services
  num = 0
  err = 0
  for item in data:

    # Debug
    logger.debug(item)

    # Capture exceptions
    try:

      if item['Amount'] > 0:

        # Create payment
        cur = dbClient.execute(con,
          '''
          INSERT INTO "Billing"."Payment"
          ("Payment_method_id", "Pos", "Customer_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" )
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
          RETURNING id
          ''',
          (
            item['Payment_method_id'] if item['Payment_method_id'] is not None else PM_CARD,
            item['Pos'],
            item['Customer_id'],
            item['Booking_id'],
            item['Amount'],
            datetime.now(),
            item['Concept'],
            'servicios'
          )
        )
        paymentid = cur.fetchone()[0]

        # Create invoice
        cur = dbClient.execute(con, 
          '''
          INSERT INTO "Billing"."Invoice"
          ("Bill_type", "Issued", "Rectified", "Issued_date", "Provider_id", "Customer_id", "Booking_id", "Payment_method_id", "Payment_id", "Concept", "Comments")
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
          RETURNING id
          ''',
          (
            'recibo' if item['Receipt'] else 'factura',
            False,
            False,
            datetime.now(),
            item['Provider_id'],
            item['Customer_id'],
            item['Booking_id'],
            item['Payment_method_id'] if item['Payment_method_id'] is not None else PM_CARD,
            paymentid,
            item['Concept'],
            item['Comments']
          )
        )
        billid = cur.fetchone()[0]

        # Create invoice line
        dbClient.execute(con, 
          '''
          INSERT INTO "Billing"."Invoice_line"
          ("Invoice_id", "Amount", "Product_id", "Tax_id", "Concept", "Comments")
          VALUES (%s, %s, %s, %s, %s, %s)
          ''',
          (
            billid,
            item['Amount'],
            item['Product_id'],
            item['Tax_id'],
            item['Concept'],
            item['Comments']
          )
        )

        # Update invoice
        dbClient.execute(con, 'UPDATE "Billing"."Invoice" SET "Issued" = %s WHERE id = %s', (True, billid))

        # Update service
        dbClient.execute(con, 'UPDATE "Booking"."Booking_service" SET "Invoice_services_id" = %s WHERE id = %s', (billid, item['id']))
        q = 1

        # Commit
        con.commit()
        num += q

    # Process exception
    except Exception as error:
      err += 1
      logger.error(error)
      con.rollback()

  # End
  logger.info('{} service invoices generated'.format(num))
  if err > 0:
    logger.error('{} service invoices not ok'.format(err))
  else:
    logger.info('{} service invoices ok'.format(err))
  return


# ###################################################
# Generate service bills for group bookints
# ###################################################

def bill_group_concepts(dbClient, con):

  # Get all non recurrent services not already billed
  cur = dbClient.execute(con,
    '''
    SELECT
      s.id, b.id as "Booking_id", b."Payer_id", b."Room_ids",
      s."Concept", s."Comments", s."Amount", s."Tax_id", s."Product_id",  s."Provider_id",
      p."Product_type_id", pr."Pos"
    FROM "Booking"."Booking_group" b
      INNER JOIN "Booking"."Booking_group_service" s ON s."Booking_id" = b.id
      INNER JOIN "Provider"."Provider" pr ON pr.id = s."Provider_id"
      INNER JOIN "Customer"."Customer" c ON b."Payer_id" = c.id
      INNER JOIN "Billing"."Product" p ON p.id = s."Product_id"
    WHERE b."Status" IN ('grupoconfirmado','inhouse')
      AND b."Date_from" <= CURRENT_DATE
      AND s."Invoice_services_id" IS NULL
      AND s."Billing_date_to" IS NULL
      AND s."Billing_date_from" <= CURRENT_DATE 
    ''')
  data = cur.fetchall()
  cur.close()

  # Loop thru services
  num = 0
  err = 0
  for item in data:

    # Debug
    logger.debug(item)

    # Capture exceptions
    try:

      if item['Amount'] > 0:

        # Group rooming list by flat
        flats = {}
        for r in item['Room_ids']:
          key = r[:12]
          if key not in flats:
            flats[key] = []
          flats[key].append(r[13:])

        # Get all flat ids
        args = tuple(flats.keys())
        cur = dbClient.execute(con, 'SELECT r."Code", id FROM "Resource"."Resource" r WHERE r."Code" IN %s ORDER BY r."Code"', (args, ))
        flat_ids = cur.fetchall()
        cur.close()

        # Create payment
        cur = dbClient.execute(con,
          '''
          INSERT INTO "Billing"."Payment"
          ("Payment_method_id", "Pos", "Customer_id", "Booking_group_id", "Amount", "Issued_date", "Concept", "Payment_type" )
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
          RETURNING id
          ''',
          (
            PM_TRANSFER,
            item['Pos'],
            item['Payer_id'],
            item['Booking_id'],
            item['Amount'],
            datetime.now(),
            item['Concept'],
            'servicios'
          )
        )
        paymentid = cur.fetchone()[0]

        # Create invoice
        cur = dbClient.execute(con, 
          '''
          INSERT INTO "Billing"."Invoice"
          ("Bill_type", "Issued", "Rectified", "Issued_date", "Provider_id", "Customer_id", "Booking_group_id", "Payment_method_id", "Payment_id", "Concept", "Comments")
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
          RETURNING id
          ''',
          (
            'factura',
            False,
            False,
            datetime.now(),
            item['Provider_id'],
            item['Payer_id'],
            item['Booking_id'],
            PM_TRANSFER,
            paymentid,
            item['Concept'],
            item['Comments']
          )
        )
        billid = cur.fetchone()[0]

        # Create invoice line
        dbClient.execute(con, 
          '''
          INSERT INTO "Billing"."Invoice_line"
          ("Invoice_id", "Resource_id", "Amount", "Product_id", "Tax_id", "Concept", "Comments")
          VALUES (%s, %s, %s, %s, %s, %s, %s)
          ''',
          (
            billid,
            flat_ids[0][1],
            item['Amount'],
            item['Product_id'],
            item['Tax_id'],
            item['Concept'],
            item['Comments']
          )
        )

        # Update invoice
        dbClient.execute(con, 'UPDATE "Billing"."Invoice" SET "Issued" = %s WHERE id = %s', (True, billid))

        # Update service
        dbClient.execute(con, 'UPDATE "Booking"."Booking_group_service" SET "Invoice_services_id" = %s WHERE id = %s', (billid, item['id']))
        q = 1

        # Commit
        con.commit()
        num += q

    # Process exception
    except Exception as error:
      err += 1
      logger.error(error)
      con.rollback()

  # End
  logger.info('{} service group invoices generated'.format(num))
  if err > 0:
    logger.error('{} service group invoices not ok'.format(err))
  else:
    logger.info('{} service group invoices ok'.format(err))
  return


# ###################################################
# Generate payments for new bills
# ###################################################

def pay_bills(dbClient, con):

  # Get all bills without payment
  cur = dbClient.execute(con,
    '''
    SELECT i.id, i."Payment_method_id", i."Customer_id", i."Booking_id", i."Booking_group_id", i."Total", i."Issued_date", i."Concept", p."Pos"
    FROM "Billing"."Invoice" i
      INNER JOIN "Provider"."Provider" p ON p.id = i."Provider_id"
    WHERE "Issued" 
      AND NOT "Rectified"
      AND "Total" > 0
      AND ("Booking_id" IS NOT NULL OR "Booking_group_id" IS NOT NULL OR "Booking_other_id" IS NOT NULL)
      AND "Payment_id" IS NULL
    ''')
  data = cur.fetchall()

  # Loop thru bills
  num = 0
  err = 0
  for item in data:

    # Debug
    logger.debug(item)

    # Capture exceptions
    try:

      cur = dbClient.execute(con,
        '''
        INSERT INTO "Billing"."Payment"
        ("Payment_method_id", "Pos", "Customer_id", "Booking_id", "Booking_group_id", "Amount", "Issued_date", "Concept", "Payment_type")
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING ID
        ''',
        (
          item['Payment_method_id'],
          item['Pos'],
          item['Customer_id'],
          item['Booking_id'],
          item['Booking_group_id'],
          item['Total'],
          item['Issued_date'],
          item['Concept'],
          'servicios'
        )
      )
      payid = cur.fetchone()[0]
       
      # Update invoice
      dbClient.execute(con, 'UPDATE "Billing"."Invoice" SET "Payment_id" = %s WHERE id = %s', (payid, item['id']))
      con.commit()
      num += 1

    # Process exception
    except Exception as error:
      err += 1
      logger.error(error)
      con.rollback()

  # End
  logger.info('{} payments generated'.format(num))
  if err > 0:
    logger.error('{} payments not ok'.format(err))
  else:
    logger.info('{} payments ok'.format(err))
  return


# ###################################################
# Generate payments for new bills
# ###################################################

def bill_lau(dbClient, con, now):

  # Get all prices not already billed
  cur = dbClient.execute(con,
    f'''
    SELECT 
      bo.id, bo."Customer_id", bo."Resource_id",
      bo."Rent", COALESCE(bo."Extras", 0) AS "Extras", bo."Extras_concept", bo."Payment_method_id", bo."Product_id",
      bo."Substatus_id", bo."Unlawful",
      r."Code", r."Owner_id",
      p."Tax_id"
    FROM "Booking"."Booking_other" bo
      INNER JOIN "Resource"."Resource" r ON r.id = bo."Resource_id" 
      INNER JOIN "Billing"."Product" p ON p.id = bo."Product_id"
      LEFT JOIN "Billing"."Invoice" i 
        ON i."Booking_other_id" = bo.id 
        AND i."Issued_date" >= DATE_TRUNC('month', '{now}'::date) 
        AND i."Issued_date" < (DATE_TRUNC('month', '{now}'::date) + INTERVAL '1 month')
    WHERE i.id IS NULL
      AND COALESCE(bo."Rent", 0) > 0
      AND (bo."Date_estimated" > '{now}'::date OR bo."Date_estimated" IS NULL)
      AND (bo."Date_bill_from" < '{now}'::date OR bo."Date_bill_from" IS NULL)
      AND (bo."Unlawful" <> TRUE OR bo."Bill_unlawful" = TRUE)
    ORDER BY 1
    ''')
  data = cur.fetchall()
  cur.close()

  # Loop thru contracts
  num = 0
  err = 0
  for item in data:

    # Debug
    logger.debug(item)

    # Capture exceptions
    try:

      # Get all non-invoiced extra concepts
      cur = dbClient.execute(con,
        '''
        SELECT s.id, s."Concept", s."Amount"
        FROM "Booking"."Booking_other_service" s
        WHERE s."Booking_id" = %s
          AND s."Billing_date" <= CURRENT_DATE
          AND s."Invoice_id" IS NULL
        ''', (item['id'], ))
      extras = cur.fetchall()
      cur.close()
      total_extras = float(sum(r['Amount'] for r in extras) or 0.0)

      # Create payment
      cur = dbClient.execute(con,
        '''
        INSERT INTO "Billing"."Payment"
        ("Payment_method_id", "Pos", "Customer_id", "Booking_other_id", "Amount", "Issued_date", "Concept", "Payment_type" )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        ''',
        (
          item['Payment_method_id'],
          'vandor',
          item['Customer_id'],
          item['id'],
          float(item['Rent']) + float(item['Extras']) + total_extras,
          now,
          'Renta mensual' if not item['Unlawful'] else 'Indemnización por ocupación inconsentida',
          'servicios'
        )
      )
      paymentid = cur.fetchone()[0]
      
      # Create invoice
      cur = dbClient.execute(con, 
        '''
        INSERT INTO "Billing"."Invoice"
        ("Bill_type", "Issued", "Rectified", "Issued_date", "Provider_id", "Customer_id", "Booking_other_id", "Payment_method_id", "Payment_id", "Concept", "Comments")
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        ''',
        (
          'factura',
          False,
          False,
          now,
          item['Owner_id'],
          item['Customer_id'],
          item['id'],
          item['Payment_method_id'],
          paymentid,
          'Renta mensual' if not item['Unlawful'] else 'Indemnización por ocupación inconsentida',
          None
        )
      )
      billid = cur.fetchone()[0]

      # Create invoice lines
      dbClient.execute(con, 
        '''
        INSERT INTO "Billing"."Invoice_line"
        ("Invoice_id", "Resource_id", "Amount", "Product_id", "Tax_id", "Concept", "Comments")
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''',
        (
          billid,
          item['Resource_id'],
          item['Rent'] + item['Extras'],
          item['Product_id'],
          item['Tax_id'],
          'Renta mensual' if not item['Unlawful'] else 'Indemnización por ocupación inconsentida',
          None
        )
      )
      for extra in extras:
        dbClient.execute(con, 
          '''
          INSERT INTO "Billing"."Invoice_line"
          ("Invoice_id", "Resource_id", "Amount", "Product_id", "Tax_id", "Concept", "Comments")
          VALUES (%s, %s, %s, %s, %s, %s, %s)
          ''',
          (
            billid,
            item['Resource_id'],
            extra['Amount'],
            item['Product_id'],
            item['Tax_id'],
            extra['Concept'],
            None
          )
        )
        dbClient.execute(con, 'UPDATE "Booking"."Booking_other_service" SET "Invoice_id" = %s WHERE id = %s', (billid ,extra['id']))

      # Update invoice
      dbClient.execute(con, 'UPDATE "Billing"."Invoice" SET "Issued" = %s WHERE id = %s', (True, billid))

      # Commit
      con.commit()
      num += 1

    # Process exception
    except Exception as error:
      err += 1
      logger.error(error)
      con.rollback()

  # End
  logger.info('{} LAU invoices generated'.format(num))
  if err > 0:
    logger.error('{} LAU invoices not ok'.format(err))
  else:
    logger.info('{} LAU inloices ok'.format(err))
  return


# ###################################################
# Billing process
# ###################################################

def main():

  # ###################################################
  # Logging
  # ###################################################

  logger.setLevel(settings.LOGLEVEL)
  formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(module)s] [%(funcName)s/%(lineno)d] [%(levelname)s] %(message)s')
  console_handler = logging.StreamHandler()
  console_handler.setLevel(settings.LOGLEVEL)
  console_handler.setFormatter(formatter)
  file_handler = RotatingFileHandler('log/batch_billing.log', maxBytes=1000000, backupCount=5)
  file_handler.setLevel(settings.LOGLEVEL)
  file_handler.setFormatter(formatter)
  logger.addHandler(console_handler)
  logger.addHandler(file_handler)
  logger.info('Started')


  # ###################################################
  # DB client
  # ###################################################

  # DB API
  dbClient = DBClient(
    host=settings.SERVER,
    port=settings.get('DBPORT', 5432),
    dbname=settings.DATABASE,
    user=settings.DBUSER,
    password=settings.DBPASS,
    sshuser=settings.SSHUSER,
    sshpassword=settings.get('SSHPASS', None),
    sshprivatekey=settings.get('SSHPKEY', None)
  )
  dbClient.connect()
  con = dbClient.getconn()


  # ###################################################
  # Main
  # ###################################################

  # Today
  now = datetime.now().strftime('%Y-%m-%d')

  # 0. Get structure data (products)
  get_data(dbClient, con)

  # 1. Generate invoice for each membership fee and deposit payment
  bill_payments(dbClient, con)

  # 2. Monthly billing process
  bill_month(dbClient, con)
  bill_group_month(dbClient, con)

  # 3. Bill extra concepts
  bill_concepts(dbClient, con)
  bill_group_concepts(dbClient, con)

  # 4. Bill LAU/Others
  bill_lau(dbClient, con, now)

  # 5. Generate payment for each manual bill
  pay_bills(dbClient, con)

  # Disconnect
  dbClient.putconn(con)
  dbClient.disconnect()


# #####################################
# Main
# #####################################

if __name__ == '__main__':

  main()
  logger.info('Finished')