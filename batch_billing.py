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
# Generate booking fee and deposit payment bills
# ###################################################

def bill_payments(dbClient):

    # Capture exceptions
    try:

        # Get all bookings without bill
        # TO DO: ordenar
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
                ("Bill_type", "Issued", "Issued_date", "Provider_id", "Customer_id", "Booking_id", "Payment_method_id", "Payment_id", "Details")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                ''', 
                (
                    'factura' if item['Payment_type'] == 'booking' else 'recibo', 
                    True, 
                    datetime.now(), 
                    1 if item['Payment_type'] == 'booking' else item['Owner_id'], 
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
                ("Invoice_id", "Amount", "Product_id", "Tax_id", "Details")
                VALUES (%s, %s, %s, %s, %s)
                ''', 
                (
                    billid, 
                    item['Amount'], 
                    1 if item['Payment_type'] == 'booking' else 2, 
                    1 if item['Payment_type'] == 'booking' else 2, 
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
        dbClient.disconnect()
        return


# ###################################################
# Generate monthly bills
# ###################################################

def bill_rent(dbClient):

    # Capture exceptions
    try:

        # Get all prices not already billed
        # TO DO: ordenar
        dbClient.select('''
        SELECT p.id, p."Booking_id", p."Rent", p."Services", p."Rent_discount", p."Services_discount", p."Rent_date", b."Customer_id", b."Payment_method_id", r."Code", r."Owner_id", r."Service_id"
        FROM "Booking"."Booking_price" p
        INNER JOIN "Booking"."Booking" b ON p."Booking_id" = b.id
        INNER JOIN "Resource"."Resource" r ON b."Resource_id" = r.id
        WHERE "Invoice_rent_id" IS NULL 
        AND "Invoice_services_id" IS NULL
        AND "Rent_date" <= %s
        ORDER BY p."Booking_id", p."Rent_date"
        ''', (datetime.now(),))
        data = dbClient.fetchall()

        # Loop thru payments
        for item in data:

            # Debug
            logger.debug(item)

            # Amounts
            rent = int(item['Rent'] or 0) + int(item['Rent_discount'] or 0)
            services = int(item['Services'] or 0) + int(item['Services_discount'] or 0)

            # Create payment
            if rent > 0 or services > 0:

                dbClient.execute('''
                    INSERT INTO "Billing"."Payment" 
                    ("Payment_method_id", "Customer_id", "Booking_id", "Amount", "Issued_date", "Concept", "Payment_type" )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    ''', 
                    (
                        item['Payment_method_id'] if item['Payment_method_id'] is not None else 1,
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
                    ("Bill_type", "Issued", "Issued_date", "Provider_id", "Customer_id", "Booking_id", "Payment_method_id", "Payment_id", "Details")
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
                        item['Payment_method_id'] if item['Payment_method_id'] is not None else 1, 
                        paymentid, 
                        'Renta mensual [' + item['Code'] + '] ' + str(item['Rent_date'])[:7]
                    )
                )
                rentid = dbClient.returning()[0]

                # Create invoice line
                dbClient.execute('''
                    INSERT INTO "Billing"."Invoice_line" 
                    ("Invoice_id", "Amount", "Product_id", "Tax_id", "Details")
                    VALUES (%s, %s, %s, %s, %s)
                    ''', 
                    (
                        rentid, 
                        rent, 
                        3, 
                        1,
                        'Renta mensual [' + item['Code'] + '] ' + str(item['Rent_date'])[:7]
                    )
                )

                # Update price
                dbClient.execute('UPDATE "Booking"."Booking_price" SET "Invoice_rent_id" = %s WHERE id = %s', (rentid, item['id']))

            # Create services invoice
            if services > 0:
                
                dbClient.execute('''
                    INSERT INTO "Billing"."Invoice" 
                    ("Bill_type", "Issued", "Issued_date", "Provider_id", "Customer_id", "Booking_id", "Payment_method_id", "Payment_id", "Details")
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
                        item['Payment_method_id'] if item['Payment_method_id'] is not None else 1, 
                        paymentid, 
                        'Servicios mensuales [' + item['Code'] + '] ' + str(item['Rent_date'])[:7]
                    )
                )
                servid = dbClient.returning()[0]

                # Create invoice line
                dbClient.execute('''
                    INSERT INTO "Billing"."Invoice_line" 
                    ("Invoice_id", "Amount", "Product_id", "Tax_id", "Details")
                    VALUES (%s, %s, %s, %s, %s)
                    ''', 
                    (
                        servid, 
                        services, 
                        4, 
                        1,
                        'Servicios mensuales [' + item['Code'] + '] ' + str(item['Rent_date'])[:7]
                    )
                )

                # Update price
                dbClient.execute('UPDATE "Booking"."Booking_price" SET "Invoice_services_id" = %s WHERE id = %s', (servid, item['id']))

        # End
        dbClient.commit()
        dbClient.disconnect()
        return

    # Process exception
    except Exception as error:
        logger.error(error)
        dbClient.rollback()
        dbClient.disconnect()
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
    #bill_rent(dbClient)


# #####################################
# Main
# #####################################

if __name__ == '__main__':

    main()