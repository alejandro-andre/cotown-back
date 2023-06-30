# ###################################################
# Batch process
# ---------------------------------------------------
# Occupancy calculation
# ###################################################

# ###################################################
# Imports
# ###################################################

# System includes
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openpyxl import load_workbook
import pandas as pd

# Cotown includes
from library.services.config import settings
from library.services.dbclient import DBClient

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Main
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
  # Lambda functions
  # ###################################################

  def nights(resource, date):

    # First and last days of the month
    mfrom = date.replace(day=1)
    mto = date + relativedelta(months=1) - relativedelta(days=1)
    
    # All bookings for the resource
    rows = df_books[df_books['Resource'] == resource]

    # Sum booked nights
    n = 0
    for _, row in rows.iterrows():
      dfrom = row['Date_from']
      dto = row['Date_to']
      if dto >= mfrom and dfrom <= mto:
        n = n + 1 + (min(mto, dto) - max(mfrom, dfrom)).days
    return n


  def available(flat, date):

    # All flat non availability rows
    rows = df_avail[df_avail['Resource_id'] == flat]

    # Check if the date is in between any range
    for _, row in rows.iterrows():
      if row['Date_from'] <= date <= row['Date_to']:
        return 0  # Not available
    return 1  # Available
  
  
  def rent(resource, date, tag):

    # All resource bills
    rows = df_bills[df_bills['Resource'] == resource]

    # Check the month
    for _, row in rows.iterrows():
      if row['Date'] == date:
        total = row[tag] + (row[tag + '_discount'] if row[tag + '_discount'] else 0)
        return int(round(total,0))
    return 0
  
  
  # ###################################################
  # 0. Preparation
  # ###################################################

  # 0.1 Get all months from 2023-01-01 to next year
  end_date = (datetime.now() + timedelta(days=366)).strftime('%Y-%m-%d')
  df_dates = pd.date_range(start='2023-01-01', end=end_date, freq='MS')

  # 0.2 Get all resources: rooms and half places
  dbClient.select('''
    SELECT b."Name" as "Building", p."Name" as "Owner", l."Name" as "Location", r."Code" as "Resource", r."Flat_id" 
    FROM "Resource"."Resource" r
    INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
    INNER JOIN "Geo"."District" d ON d.id = b."District_id"
    INNER JOIN "Geo"."Location" l on l.id = d."Location_id"
    INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id"
    WHERE ("Resource_type" = 'habitacion' OR r."Code" LIKE '%.P2')
  ''')
  columns = [desc[0] for desc in dbClient.sel.description]
  df_res = pd.DataFrame.from_records(dbClient.fetchall(), columns=columns)


  # ###################################################
  # 1. Beds
  # ###################################################

  # 1.1 Get all unavailabilities
  dbClient.select('SELECT "Resource_id", "Date_from", "Date_to" FROM "Resource"."Resource_availability"')
  columns = [desc[0] for desc in dbClient.sel.description]
  df_avail = pd.DataFrame.from_records(dbClient.fetchall(), columns=columns)

  # 1.2. Check available resources (beds) by month
  df_beds = df_res.copy()
  for date in df_dates:
    dt = date.date()
    df_beds[dt] = df_beds.apply(lambda row: available(row['Flat_id'], dt), axis=1)
  df_beds.drop('Flat_id', axis=1, inplace=True)
  df_res.drop('Flat_id', axis=1, inplace=True)


  # ###################################################
  # 2. Income
  # ###################################################

  # 2.1. Get all rents
  dbClient.select('''
    SELECT x."Code" AS "Resource", DATE_TRUNC('month', x."Rent_date") as "Date", 
	         SUM(x."Rent") AS "Rent", SUM(x."Rent_discount") AS "Rent_discount",
           SUM(x."Services") AS "Services", SUM(x."Services_discount") AS "Services_discount"
    FROM (
      SELECT r."Code", bp."Rent_date", bg."Rent", 0 AS "Rent_discount", bg."Services", 0 AS "Services_discount"
      FROM "Booking"."Booking_group" bg 
      INNER JOIN "Booking"."Booking_group_price" bp ON bp."Booking_id" = bg.id
      INNER JOIN "Booking"."Booking_rooming" br ON br."Booking_id" = bg.id
      INNER JOIN "Resource"."Resource" r ON r.id = br."Resource_id"
      UNION
      SELECT r."Code", bp."Rent_date", bp."Rent", bp."Rent_discount", bp."Services", bp."Services_discount"
      FROM "Booking"."Booking_price" bp
      INNER JOIN "Booking"."Booking" b ON b.id = bp."Booking_id"
      INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
    ) AS x
    GROUP BY 1, 2;
  ''')
  columns = [desc[0] for desc in dbClient.sel.description]
  df_bills = pd.DataFrame.from_records(dbClient.fetchall(), columns=columns)
  df_bills['Date'] = df_bills['Date'].dt.date

  # # 2.2. Pivot rent income by month
  df_rent = df_res.copy()
  for date in df_dates:
    dt = date.date()
    df_rent[dt] = df_rent.apply(lambda row: rent(row['Resource'], dt, "Rent"), axis=1)

  # # 2.3. Pivot services income by month
  df_service = df_res.copy()
  for date in df_dates:
    dt = date.date()
    df_service[dt] = df_service.apply(lambda row: rent(row['Resource'], dt, "Services"), axis=1)


  # ###################################################
  # 3. Room nights
  # ###################################################

  # 3.1. Get all bookings
  dbClient.select('''
    SELECT r."Code" AS "Resource", b."Date_from", b."Date_to"
    FROM "Booking"."Booking" b
    INNER JOIN "Resource"."Resource" r ON r.id = b."Resource_id"
    UNION
    SELECT "Code" AS "Resource", "Date_from", "Date_to"
    FROM "Booking"."Booking_group" bg 
    INNER JOIN "Booking"."Booking_rooming" br ON bg.id = br."Booking_id"
    INNER JOIN "Resource"."Resource" r ON r.id = br."Resource_id";
  ''')
  columns = [desc[0] for desc in dbClient.sel.description]
  df_books = pd.DataFrame.from_records(dbClient.fetchall(), columns=columns)

  # 3.2. Pivot booked room nights by month
  df_night = df_res.copy()
  for date in df_dates:
    dt = date.date()
    df_night[dt] = df_night.apply(lambda row: nights(row['Resource'], dt), axis=1)


  # ###################################################
  # Final. To excel
  # ###################################################

  # Write data
  book = load_workbook('templates/occupancy-report.xlsx')
  book.save('occupancy.xlsx')
  with pd.ExcelWriter('occupancy.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_beds.to_excel(writer, sheet_name='data-beds', index=False)
    df_night.to_excel(writer, sheet_name='data-nights', index=False)
    df_rent.to_excel(writer, sheet_name='data-rent', index=False)
    df_service.to_excel(writer, sheet_name='data-services', index=False)


# #####################################
# Main
# #####################################

if __name__ == '__main__':

  main()
  logger.info('Finished')
