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
PR_RENT_SERVICES = 5

VAT_21 = 1
VAT_0  = 2

PRODUCTS = {}

# ###################################################
# Get structure data
# ###################################################

def get_data(dbClient):

  # Capture exceptions
  try:

    # Get all payments without bill
    dbClient.select('''
      SELECT p.id, p."Name", p."Name_en", t.id, t."Name", t."Name_en", t."Value" 
      FROM "Billing"."Product" p
      INNER JOIN "Billing"."Tax" t ON t.id = p."Tax_id";
    ''')
    data = dbClient.fetchall()
    for product in data:
      PRODUCTS[product[0]] = {
        'concept': product[1],
        'tax': product[3],
        'value': product[5]
      }

  except Exception as error:
    logger.error(error)
    dbClient.rollback()


# ###################################################
# Generate booking fee and deposit payment bills
# ###################################################

def bill_payments(dbClient):

  # Get all payments without bill
  dbClient.select('''
    SELECT p.id, p."Payment_type", p."Customer_id", p."Booking_id", p."Payment_method_id", p."Amount", r."Owner_id", r."Code"
    FROM "Billing"."Payment" p
    INNER JOIN "Booking"."Booking" b ON p."Booking_id" = b.id
    LEFT JOIN "Resource"."Resource" r ON b."Resource_id" = r.id
    LEFT JOIN "Billing"."Invoice" i ON i."Payment_id" = p.id
    WHERE "Payment_date" IS NOT NULL
    AND i.id IS NULL
    ORDER BY p."Booking_id"
  ''')
  data = dbClient.fetchall()

  # Loop thru payments
  num = 0
  err = 0
  for item in data:

    # Debug
    logger.debug(item)

    # Capture exceptions
    try:

      # Create invoice
      dbClient.execute('''
        INSERT INTO "Billing"."Invoice" 
        ("Bill_type", "Issued", "Rectified", "Issued_date", "Provider_id", "Customer_id", "Booking_id", "Payment_method_id", "Payment_id", "Concept")
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        ''', 
        (
          'recibo' if item['Payment_type'] == 'deposito' else 'factura', 
          False, 
          False,
          datetime.now(), 
          ID_COTOWN if item['Payment_type'] == 'booking' else item['Owner_id'], 
          item['Customer_id'], 
          item['Booking_id'], 
          item['Payment_method_id'], 
          item['id'],
          PRODUCTS[PR_BOOKING_FEE]['concept'] if item['Payment_type'] == 'booking' else PRODUCTS[PR_DEPOSIT]['concept'], 
        )
      )
      billid = dbClient.returning()[0]

      # Create invoice line
      dbClient.execute('''
        INSERT INTO "Billing"."Invoice_line" 
        ("Invoice_id", "Amount", "Product_id", "Tax_id", "Concept")
        VALUES (%s, %s, %s, %s, %s)
        ''', 
        (
          billid, 
          item['Amount'], 
          PR_BOOKING_FEE if item['Payment_type'] == 'booking' else PR_DEPOSIT, 
          PR_BOOKING_FEE if item['Payment_type'] == 'booking' else PR_DEPOSIT,
          PRODUCTS[PR_BOOKING_FEE]['concept'] if item['Payment_type'] == 'booking' else PRODUCTS[PR_DEPOSIT]['concept'] + ' ' + item['Code']
        )
      )

      # Update bill
      dbClient.execute('UPDATE "Billing"."Invoice" SET "Issued" = %s WHERE id = %s', (True, billid))
      dbClient.commit()
      num += 1

    # Process exception
    except Exception as error:
      err += 1
      logger.error(error)
      dbClient.rollback()

  # End
  logger.info('{} payment bills generated'.format(num))
  logger.info('{} payment bills with error'.format(err))
  return

# ###################################################
# Generate monthly bills
# ###################################################

def bill_rent(dbClient):

  # Get all prices not already billed
  dbClient.select('''
  SELECT p.id, p."Booking_id", p."Rent", p."Services", p."Rent_discount", p."Services_discount", p."Rent_date", 
          b."Customer_id", b."Payment_method_id", r."Code", r."Owner_id", r."Service_id", st."Tax_id"
  FROM "Booking"."Booking_price" p
  INNER JOIN "Booking"."Booking" b ON p."Booking_id" = b.id
  INNER JOIN "Resource"."Resource" r ON b."Resource_id" = r.id
  INNER JOIN "Building"."Building" bu ON bu.id = r."Building_id"
  INNER JOIN "Building"."Building_type" st ON st.id = bu."Building_type_id" 
  WHERE b."Status" IN ('checkin', 'inhouse','checkout')
  AND "Invoice_rent_id" IS NULL 
  AND "Invoice_services_id" IS NULL
  AND "Rent_date" <= %s
  AND "Rent_date" >= %s
  ''', (datetime.now(), settings.BILLDATE))
  data = dbClient.fetchall()

  # Loop thru payments
  num = 0
  err = 0
  for item in data:

    # Debug
    logger.debug(item)

    # Capture exceptions
    try:

      # Amounts
      rent = int(item['Rent'] or 0) + int(item['Rent_discount'] or 0)
      services = int(item['Services'] or 0) + int(item['Services_discount'] or 0)

      # Same issuer
      product = PRODUCTS[PR_RENT]
      if item['Owner_id'] == item['Service_id']:
        product = PRODUCTS[PR_RENT_SERVICES]
        rent += services
        services = 0
        
      # Create payment
      if rent > 0 or services > 0:

        dbClient.execute('''
          INSERT INTO "Billing"."Payment" 
          ("Payment_method_id", "Customer_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" )
          VALUES (%s, %s, %s, %s, %s, %s, %s)
          RETURNING id
          ''', 
          (
            item['Payment_method_id'] if item['Payment_method_id'] is not None else PM_CARD,
            item['Customer_id'], 
            item['Booking_id'], 
            rent + services,
            datetime.now(), 
            product['concept'] + ' [' + item['Code'] + '] ' + str(item['Rent_date']),
            'servicios'
          )
        )
        paymentid = dbClient.returning()[0]

        # Create rent invoice
        if rent > 0:

          dbClient.execute('''
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
              item['Owner_id'], 
              item['Customer_id'], 
              item['Booking_id'], 
              item['Payment_method_id'] if item['Payment_method_id'] is not None else PM_CARD, 
              paymentid, 
              product['concept'] + ' [' + item['Code'] + '] ' + str(item['Rent_date'])[:7]
            )
          )
          rentid = dbClient.returning()[0]

          # Create invoice line
          dbClient.execute('''
            INSERT INTO "Billing"."Invoice_line" 
            ("Invoice_id", "Amount", "Product_id", "Tax_id", "Concept")
            VALUES (%s, %s, %s, %s, %s)
            ''', 
            (
              rentid, 
              rent, 
              PR_RENT, 
              product['tax'] if item['Tax_id'] is None else item['Tax_id'],
              product['concept'] + ' [' + item['Code'] + '] ' + str(item['Rent_date'])[:7]
            )
          )

          # Update bill
          dbClient.execute('UPDATE "Billing"."Invoice" SET "Issued" = %s WHERE id = %s', (True, rentid))

          # Update price
          dbClient.execute('UPDATE "Booking"."Booking_price" SET "Invoice_rent_id" = %s WHERE id = %s', (rentid, item['id']))

        # Create services invoice
        if services > 0:
          
          dbClient.execute('''
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
          servid = dbClient.returning()[0]

          # Create invoice line
          dbClient.execute('''
            INSERT INTO "Billing"."Invoice_line" 
            ("Invoice_id", "Amount", "Product_id", "Tax_id", "Concept")
            VALUES (%s, %s, %s, %s, %s)
            ''', 
            (
              servid, 
              services, 
              PR_SERVICES, 
              PRODUCTS[PR_SERVICES]['tax'],
              PRODUCTS[PR_SERVICES]['concept'] + ' [' + item['Code'] + '] ' + str(item['Rent_date'])[:7]
            )
          )

          # Update bill
          dbClient.execute('UPDATE "Billing"."Invoice" SET "Issued" = %s WHERE id = %s', (True, servid))

          # Update price
          dbClient.execute('UPDATE "Booking"."Booking_price" SET "Invoice_services_id" = %s WHERE id = %s', (servid, item['id']))

        # Commit
        dbClient.commit()
        num += 1

    # Process exception
    except Exception as error:
      err += 1
      logger.error(error)
      dbClient.rollback()

  # End
  logger.info('{} bills generated'.format(num))
  logger.info('{} bills with error'.format(err))
  return



# ###################################################
# Generate monthly bills for group bookints
# ###################################################

def bill_group_rent(dbClient):

  # Get all prices not already billed
  dbClient.select('''
  SELECT bgp.id, bgp."Booking_id", bgp."Rent_date", bgp."Rent", bgp."Services", bg."Payer_id", bg."Tax", COUNT(r."Code") as num, MAX(r."Owner_id") as "Owner_id", MAX(r."Service_id") as "Service_id"
  FROM "Booking"."Booking_group_price" bgp
  INNER JOIN "Booking"."Booking_group" bg ON bg.id = bgp."Booking_id"
  INNER JOIN "Booking"."Booking_rooming" br ON bg.id = br."Booking_id"
  INNER JOIN "Resource"."Resource" r ON r.id = br."Resource_id" 
  WHERE bg."Status" = 'grupoconfirmado'
  AND bgp."Invoice_rent_id" IS NULL
  AND bgp."Rent_date" <= %s
  AND bgp."Rent_date" >= %s
  GROUP BY bgp.id, bgp."Booking_id", bgp."Rent_date", bgp."Rent", bgp."Services", bg."Payer_id", bg."Tax"
  ORDER BY bgp."Booking_id", bgp."Rent_date"
  ''', (datetime.now(), settings.BILLDATE, ))
  data = dbClient.fetchall()

  # Loop thru payments
  num = 0
  err = 0
  for item in data:

    # Debug
    logger.debug(item)

    # Capture exceptions
    try:

      # Amounts
      rent = int(item['Rent'] or 0) * int(item['num'] or 0)
      services = int(item['Services'] or 0) * int(item['num'] or 0)

      # Create payment
      if rent + services > 0:

        dbClient.execute('''
          INSERT INTO "Billing"."Payment" 
          ("Payment_method_id", "Customer_id", "Booking_group_id", "Amount", "Issued_date", "Concept", "Payment_type" )
          VALUES (%s, %s, %s, %s, %s, %s, %s)
          RETURNING id
          ''', 
          (
            PM_TRANSFER,
            item['Payer_id'], 
            item['Booking_id'], 
            rent + services,
            datetime.now(), 
            'Renta y servicios (' + str(item['num']) + ' plazas) ' + str(item['Rent_date'])[:7],
            'servicios'
          )
        )
        paymentid = dbClient.returning()[0]

        # Create rent invoice
        if rent > 0:

          dbClient.execute('''
            INSERT INTO "Billing"."Invoice" 
            ("Bill_type", "Issued", "Rectified", "Issued_date", "Provider_id", "Customer_id", "Booking_group_id", "Payment_method_id", "Payment_id", "Concept")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            ''', 
            (
              'factura', 
              False, 
              False,
              datetime.now(), 
              item['Owner_id'], 
              item['Payer_id'], 
              item['Booking_id'], 
              PM_TRANSFER, 
              paymentid, 
              'Renta mensual (' + str(item['num']) + ' plazas) ' + str(item['Rent_date'])[:7],
            )
          )
          rentid = dbClient.returning()[0]

          # Create invoice line
          dbClient.execute('''
            INSERT INTO "Billing"."Invoice_line" 
            ("Invoice_id", "Amount", "Product_id", "Tax_id", "Concept")
            VALUES (%s, %s, %s, %s, %s)
            ''', 
            (
              rentid, 
              rent, 
              PR_RENT,
              PRODUCTS[PR_RENT]['tax'] if item['Tax'] else VAT_21,
              'Renta mensual (' + str(item['num']) + ' plazas) ' + str(item['Rent_date'])[:7],
            )
          )

          # Update bill
          dbClient.execute('UPDATE "Billing"."Invoice" SET "Issued" = %s WHERE id = %s', (True, rentid))

          # Update price
          dbClient.execute('UPDATE "Booking"."Booking_group_price" SET "Invoice_rent_id" = %s WHERE id = %s', (rentid, item['id']))

        # Create services invoice
        if services > 0:
          
          dbClient.execute('''
            INSERT INTO "Billing"."Invoice" 
            ("Bill_type", "Issued", "Rectified", "Issued_date", "Provider_id", "Customer_id", "Booking_group_id", "Payment_method_id", "Payment_id", "Concept")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
              'Servicios mensuales (' + str(item['num']) + ' plazas) ' + str(item['Rent_date'])[:7],
            )
          )
          servid = dbClient.returning()[0]

          # Create invoice line
          dbClient.execute('''
            INSERT INTO "Billing"."Invoice_line" 
            ("Invoice_id", "Amount", "Product_id", "Tax_id", "Concept")
            VALUES (%s, %s, %s, %s, %s)
            ''', 
            (
              servid, 
              services, 
              PR_SERVICES, 
              VAT_0 if item['Tax'] else VAT_21,
              'Servicios mensuales (' + str(item['num']) + ' plazas) ' + str(item['Rent_date'])[:7],
            )
          )

          # Update bill
          dbClient.execute('UPDATE "Billing"."Invoice" SET "Issued" = %s WHERE id = %s', (True, servid))

          # Update price
          dbClient.execute('UPDATE "Booking"."Booking_group_price" SET "Invoice_services_id" = %s WHERE id = %s', (servid, item['id']))

        # Commit
        dbClient.commit()
        num += 1
            
    # Process exception
    except Exception as error:
      err += 1
      logger.error(error)
      dbClient.rollback()

  # End
  logger.info('{} group bills generated'.format(num))
  logger.info('{} group bills with error'.format(err))
  return



# ###################################################
# Generate monthly bills for group bookints
# ###################################################

def pay_bills(dbClient):

  # Get all bills without payment
  dbClient.select('''
  SELECT id, "Payment_method_id", "Customer_id", "Booking_id", "Booking_group_id", "Total", "Issued_date", "Concept"
  FROM "Billing"."Invoice" 
  WHERE "Issued" AND "Payment_id" IS NULL''')
  data = dbClient.fetchall()

  # Loop thru bills
  num = 0
  err = 0
  for item in data:

    # Debug
    logger.debug(item)

    # Capture exceptions
    try:

      dbClient.execute('''
        INSERT INTO "Billing"."Payment" 
        ("Payment_method_id", "Customer_id", "Booking_id", "Booking_group_id", "Amount", "Issued_date", "Concept", "Payment_type")
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING ID
        ''', 
        (
          item['Payment_method_id'],
          item['Customer_id'], 
          item['Booking_id'], 
          item['Booking_group_id'], 
          item['Total'], 
          item['Issued_date'], 
          item['Concept'], 
          'servicios'
        )
      )
      payid = dbClient.returning()[0]
        
      # Update bill
      dbClient.execute('UPDATE "Billing"."Invoice" SET "Payment_id" = %s WHERE id = %s', (payid, item['id']))
      dbClient.commit()
      num += 1

    # Process exception
    except Exception as error:
      err += 1
      logger.error(error)
      dbClient.rollback()

  # End
  dbClient.commit()
  logger.info('{} payments generated'.format(num))
  logger.info('{} payments with error'.format(err))
  return



# ###################################################
# Billing process
# ###################################################

def main():

  # ###################################################
  # Logging
  # ###################################################

  logger.setLevel(settings.LOGLEVEL)
  console_handler = logging.StreamHandler()
  console_handler.setLevel(settings.LOGLEVEL)
  formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(module)s] [%(funcName)s/%(lineno)d] [%(levelname)s] %(message)s')
  console_handler.setFormatter(formatter)
  logger.addHandler(console_handler)
  logger.info('Started')


  # ###################################################
  # DB client
  # ###################################################

  # DB API
  dbClient = DBClient(settings.SERVER, settings.DATABASE, settings.DBUSER, settings.DBPASS, settings.SSHUSER, settings.SSHPASS)
  dbClient.connect()


  # ###################################################
  # Main
  # ###################################################

  # 0. Get structure data
  get_data(dbClient)

  # 1. Generate invoice for each booking fee and deposit payment 
  bill_payments(dbClient)

  # 2. Monthly billing process
  bill_rent(dbClient)
  bill_group_rent(dbClient)

  # 3. Generate payment for each manual bill
  pay_bills(dbClient)

  # Disconnect
  dbClient.connect()


# #####################################
# Main
# #####################################

if __name__ == '__main__':

  main()
  logger.info('Finished')
