# ###################################################
# Batch process
# ---------------------------------------------------
# Billing process
# ###################################################

# ###################################################
# Imports
# ###################################################

# System includes
import os
from datetime import datetime

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Cotown includes
from library.services.dbclient import DBClient


# ###################################################
# Constants
# ###################################################

START_DATE = '2023-05-01'

ID_COTOWN = 1

PM_CARD = 1
PM_TRANSFER = 2

PR_BOOKING_FEE = 1
PR_DEPOSIT = 2
PR_RENT = 3
PR_SERVICES = 4

VAT_21 = 1
VAT_0 = 2

# ###################################################
# Generate booking fee and deposit payment bills
# ###################################################

def bill_payments(dbClient):

  # Capture exceptions
  try:

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
    for item in data:

      # Debug
      logger.debug(item)

      # Create invoice
      dbClient.execute('''
        INSERT INTO "Billing"."Invoice" 
        ("Bill_type", "Issued", "Issued_date", "Provider_id", "Customer_id", "Booking_id", "Payment_method_id", "Payment_id", "Concept")
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        ''', 
        (
          'factura' if item['Payment_type'] == 'booking' else 'recibo', 
          True, 
          datetime.now(), 
          ID_COTOWN if item['Payment_type'] == 'booking' else item['Owner_id'], 
          item['Customer_id'], 
          item['Booking_id'], 
          item['Payment_method_id'], 
          item['id'], 
          'Booking fee' if item['Payment_type'] == 'booking' else 'Garantía', 
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
          'Booking fee' if item['Payment_type'] == 'booking' else 'Garantía ' + item['Code'],
        )
      )

    # End
    dbClient.commit()
    return

  # Process exception
  except Exception as error:
    logger.error(error)
    dbClient.rollback()
    return


# ###################################################
# Generate monthly bills
# ###################################################

def bill_rent(dbClient):

  # Capture exceptions
  try:

    # Get all prices not already billed
    dbClient.select('''
    SELECT p.id, p."Booking_id", p."Rent", p."Services", p."Rent_discount", p."Services_discount", p."Rent_date", b."Customer_id", b."Payment_method_id", r."Code", r."Owner_id", r."Service_id"
    FROM "Booking"."Booking_price" p
    INNER JOIN "Booking"."Booking" b ON p."Booking_id" = b.id
    INNER JOIN "Resource"."Resource" r ON b."Resource_id" = r.id
    WHERE "Invoice_rent_id" IS NULL 
    AND "Invoice_services_id" IS NULL
    AND "Rent_date" <= %s
    AND "Rent_date" >= %s
    ORDER BY p."Booking_id", p."Rent_date"
    ''', (datetime.now(), START_DATE))
    data = dbClient.fetchall()

    # Loop thru payments
    for item in data:

      # Debug
      logger.debug(item)

      # Amounts
      rent = int(item['Rent'] or 0) + int(item['Rent_discount'] or 0)
      services = int(item['Services'] or 0) + int(item['Services_discount'] or 0)

      # Same issuer
      if item['Owner_id'] == item['Service_id']:
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
            'Renta y servicios ' + item['Code'] + ' ' + str(item['Rent_date']),
            'servicios'
          )
        )
        paymentid = dbClient.returning()[0]

      # Create rent invoice
      if rent > 0:

        dbClient.execute('''
          INSERT INTO "Billing"."Invoice" 
          ("Bill_type", "Issued", "Issued_date", "Provider_id", "Customer_id", "Booking_id", "Payment_method_id", "Payment_id", "Concept")
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
          RETURNING id
          ''', 
          (
            'factura', 
            True, 
            datetime.now(), 
            item['Owner_id'], 
            item['Customer_id'], 
            item['Booking_id'], 
            item['Payment_method_id'] if item['Payment_method_id'] is not None else PM_CARD, 
            paymentid, 
            'Renta mensual [' + item['Code'] + '] ' + str(item['Rent_date'])[:7]
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
            VAT_0,
            'Renta mensual [' + item['Code'] + '] ' + str(item['Rent_date'])[:7]
          )
        )

        # Update price
        dbClient.execute('UPDATE "Booking"."Booking_price" SET "Invoice_rent_id" = %s WHERE id = %s', (rentid, item['id']))

      # Create services invoice
      if services > 0:
        
        dbClient.execute('''
          INSERT INTO "Billing"."Invoice" 
          ("Bill_type", "Issued", "Issued_date", "Provider_id", "Customer_id", "Booking_id", "Payment_method_id", "Payment_id", "Concept")
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
          RETURNING id
          ''', 
          (
            'factura', 
            True, 
            datetime.now(), 
            item['Service_id'], 
            item['Customer_id'], 
            item['Booking_id'], 
            item['Payment_method_id'] if item['Payment_method_id'] is not None else PM_CARD, 
            paymentid, 
            'Servicios mensuales [' + item['Code'] + '] ' + str(item['Rent_date'])[:7]
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
            VAT_21,
            'Servicios mensuales [' + item['Code'] + '] ' + str(item['Rent_date'])[:7]
          )
        )

        # Update price
        dbClient.execute('UPDATE "Booking"."Booking_price" SET "Invoice_services_id" = %s WHERE id = %s', (servid, item['id']))

    # End
    dbClient.commit()
    return

  # Process exception
  except Exception as error:
    logger.error(error)
    dbClient.rollback()
    return


# ###################################################
# Generate monthly bills for group bookints
# ###################################################

def bill_group_rent(dbClient):

  # Capture exceptions
  try:

    # Get all prices not already billed
    dbClient.select('''
    SELECT bgp.id, bgp."Booking_id", bgp."Rent_date", bgp."Rent", bgp."Services", bg."Payer_id", bg."Tax", COUNT(r."Code") as num, MAX(r."Owner_id") as "Owner_id", MAX(r."Service_id") as "Service_id"
    FROM "Booking"."Booking_group_price" bgp
    INNER JOIN "Booking"."Booking_group" bg ON bg.id = bgp."Booking_id"
    INNER JOIN "Booking"."Booking_rooming" br ON bg.id = br."Booking_id"
    INNER JOIN "Resource"."Resource" r ON r.id = br."Resource_id" 
    WHERE bgp."Invoice_rent_id" IS NULL
    AND bgp."Rent_date" <= %s
    AND bgp."Rent_date" >= %s
    GROUP BY bgp.id, bgp."Booking_id", bgp."Rent_date", bgp."Rent", bgp."Services", bg."Payer_id", bg."Tax"
    ORDER BY bgp."Booking_id", bgp."Rent_date"
    ''', (datetime.now(), START_DATE, ))
    data = dbClient.fetchall()

    # Loop thru payments
    for item in data:

      # Debug
      logger.debug(item)

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
          ("Bill_type", "Issued", "Issued_date", "Provider_id", "Customer_id", "Booking_group_id", "Payment_method_id", "Payment_id", "Concept")
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
          RETURNING id
          ''', 
          (
            'factura', 
            True, 
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
            VAT_0 if item['Tax'] else VAT_21,
            'Renta mensual (' + str(item['num']) + ' plazas) ' + str(item['Rent_date'])[:7],
          )
        )

        # Update price
        dbClient.execute('UPDATE "Booking"."Booking_group_price" SET "Invoice_rent_id" = %s WHERE id = %s', (rentid, item['id']))

      # Create services invoice
      if services > 0:
        
        dbClient.execute('''
          INSERT INTO "Billing"."Invoice" 
          ("Bill_type", "Issued", "Issued_date", "Provider_id", "Customer_id", "Booking_group_id", "Payment_method_id", "Payment_id", "Concept")
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
          RETURNING id
          ''', 
          (
            'factura', 
            True, 
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

        # Update price
        dbClient.execute('UPDATE "Booking"."Booking_group_price" SET "Invoice_services_id" = %s WHERE id = %s', (servid, item['id']))
        
    # End
    dbClient.commit()
    return

  # Process exception
  except Exception as error:
    logger.error(error)
    dbClient.rollback()
    return


# ###################################################
# Billing process
# ###################################################

def main():

  # ###################################################
  # Logging
  # ###################################################

  logger.setLevel(logging.DEBUG)
  console_handler = logging.StreamHandler()
  console_handler.setLevel(logging.DEBUG)
  formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(module)s] [%(levelname)s] %(message)s')
  console_handler.setFormatter(formatter)
  logger.addHandler(console_handler)
  logger.info('Started')


  # ###################################################
  # Environment variables
  # ###################################################

  SERVER   = str(os.environ.get('COTOWN_SERVER'))
  DATABASE = str(os.environ.get('COTOWN_DATABASE'))
  DBUSER   = str(os.environ.get('COTOWN_DBUSER'))
  DBPASS   = str(os.environ.get('COTOWN_DBPASS'))
  SSHUSER  = str(os.environ.get('COTOWN_SSHUSER'))
  SSHPASS  = str(os.environ.get('COTOWN_SSHPASS'))


  # ###################################################
  # DB client
  # ###################################################

  # DB API
  dbClient = DBClient(SERVER, DATABASE, DBUSER, DBPASS, SSHUSER, SSHPASS)
  dbClient.connect()


  # ###################################################
  # Main
  # ###################################################

  # 1. Generate invoice for each booking fee and deposit payment 
  bill_payments(dbClient)

  # 2. Monthly billing process
  bill_rent(dbClient)
  bill_group_rent(dbClient)

  # Disconnect
  dbClient.connect()


# #####################################
# Main
# #####################################

if __name__ == '__main__':

  main()