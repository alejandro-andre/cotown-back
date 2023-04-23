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
from library.services.apiclient import APIClient
from library.services.dbclient import DBClient


# ###################################################
# Generate booking fee and deposit payment bills
# ###################################################

def bill_payments(dbClient):

    # Capture exceptions
    try:

        # Get all bookings without bill
        dbClient.select('''
            SELECT p.id, p."Payment_type", p."Customer_id", p."Booking_id", p."Payment_method_id", p."Amount", r."Owner_id" 
            FROM "Billing"."Payment" p
            INNER JOIN "Booking"."Booking" b ON p."Booking_id" = b.id
            INNER JOIN "Resource"."Resource" r ON b."Resource_id" = r.id
            LEFT JOIN "Billing"."Invoice" i ON i."Payment_id" = b.id
            WHERE "Payment_date" IS NOT NULL
            AND i.id IS NULL
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
                ("Invoice_id", "Amount", "Product_id", "Tax_id")
                VALUES (%s, %s, %s, %s)
                ''', 
                (
                    billid, 
                    item['Amount'], 
                    1 if item['Payment_type'] == 'booking' else 2, 
                    1 if item['Payment_type'] == 'booking' else 2, 
                )
            )

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
# Generate monthly bills
# ###################################################

def bill_rent(dbClient):
    
    pass


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


# #####################################
# Main
# #####################################

if __name__ == '__main__':

    main()