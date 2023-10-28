# ###################################################
# Imports
# ###################################################

# System includes
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openpyxl import load_workbook
from openpyxl.formula.translate import Translator
import pandas as pd
import tempfile

# Cotown includes
from library.services.config import settings
from library.services.dbclient import DBClient

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Main
# ###################################################

def do_occupancy(dbClient, vars):

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

  # Connect
  logger.info('Start occupancy report')
  dbClient.connect()

  # 0.1 Get all months from the selected range
  # http://localhost:5000/api/v1/occupancy?fdesde=2023-01-01&fhasta=2024-12-31
  start_date = '2023-01-01'
  if vars.get('fdesde'):
    start_date = vars.get('fdesde')
  end_date = (datetime.now() + timedelta(days=366)).strftime('%Y-%m-%d')
  if vars.get('fhasta'):
    end_date = vars.get('fhasta')
  df_dates = pd.date_range(start=start_date, end=end_date, freq='MS')

  # 0.2 Get all resources: individual rooms and places
  dbClient.select('''
    SELECT b."Name" as "Building", p."Name" as "Owner", l."Name" as "Location", r."Code" as "Resource", r."Flat_id" 
    FROM "Resource"."Resource" r
    INNER JOIN "Building"."Building" b ON b.id = r."Building_id"
    INNER JOIN "Geo"."District" d ON d.id = b."District_id"
    INNER JOIN "Geo"."Location" l on l.id = d."Location_id"
    INNER JOIN "Provider"."Provider" p ON p.id = r."Owner_id"
    WHERE NOT EXISTS (SELECT id FROM "Resource"."Resource" rr WHERE rr."Code" LIKE CONCAT(r."Code", '.%'))
    ORDER BY r."Code" ASC;
  ''')
  columns = [desc[0] for desc in dbClient.sel.description]
  df_res = pd.DataFrame.from_records(dbClient.fetchall(), columns=columns)
  logger.info('Resources retrieved')


  # ###################################################
  # 1. Beds
  # ###################################################

  # 1.1 Get all unavailabilities that affect stock
  dbClient.select('''
  SELECT "Resource_id", "Date_from", "Date_to" 
  FROM "Resource"."Resource_availability" ra
  INNER JOIN "Resource"."Resource_status" rs ON rs.id = ra."Status_id"
  WHERE NOT rs."Available"
  ''')
  columns = [desc[0] for desc in dbClient.sel.description]
  df_avail = pd.DataFrame.from_records(dbClient.fetchall(), columns=columns)
  logger.info('Unavailabilities retrieved')

  # 1.2. Check available resources (beds) by month
  df_beds = df_res.copy()
  for date in df_dates:
    dt = date.date()
    df_beds[dt] = df_beds.apply(lambda row: available(row['Flat_id'], dt), axis=1)
  df_beds.drop('Flat_id', axis=1, inplace=True)
  df_res.drop('Flat_id', axis=1, inplace=True)
  logger.info('Beds calculated')


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
  if len(df_bills.index) > 0:
    df_bills['Date'] = df_bills['Date'].dt.date
  logger.info('Prices retrieved')

  # # 2.2. Pivot rent income by month
  df_rent = df_res.copy()
  for date in df_dates:
    dt = date.date()
    df_rent[dt] = df_rent.apply(lambda row: rent(row['Resource'], dt, "Rent"), axis=1)
  logger.info('Rent calculated')

  # # 2.3. Pivot services income by month
  df_service = df_res.copy()
  for date in df_dates:
    dt = date.date()
    df_service[dt] = df_service.apply(lambda row: rent(row['Resource'], dt, "Services"), axis=1)
  logger.info('Services calculated')


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
  logger.info('Bookings retrieved')

  # 3.2. Pivot booked room nights by month
  df_night = df_res.copy()
  for date in df_dates:
    dt = date.date()
    df_night[dt] = df_night.apply(lambda row: nights(row['Resource'], dt), axis=1)
  logger.info('Nights calculated')


  # ###################################################
  # Final. To excel
  # ###################################################

  # Generate new book from template
  book = load_workbook('templates/report/occupancy.xlsx')
  logger.info('Template loaded')

  # Replicate columns
  for sheet_name in book.sheetnames:

    # Only dashboard sheets
    if 'data-' not in sheet_name:
      sheet = book[sheet_name]

      # One column per date
      for i, _ in enumerate(df_dates):
        if i > 0:

          # Copy column formulas and styles
          for row in range(1, sheet.max_row+1):
            src = sheet.cell(row=row, column=2)
            if src.data_type == 'f':
              t = Translator(src.value, 'A1')
              formula  = t.translate_formula(col_delta=i)
            else:
              formula = src.value
            dst = sheet.cell(row=row, column=2+i, value=formula)
            dst._style = src._style

      # Today's date
      sheet.cell(row=1, column=2, value=datetime.now().date())

  # Save book
  temp = tempfile.NamedTemporaryFile(suffix='.xlsx').name
  book.save(temp)
  logger.info('Template prepared')

  # Write data
  with pd.ExcelWriter(temp, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:

    # Write sheets
    df_beds.to_excel(writer, sheet_name='data-beds', index=False)
    df_night.to_excel(writer, sheet_name='data-nights', index=False)
    df_rent.to_excel(writer, sheet_name='data-rent', index=False)
    df_service.to_excel(writer, sheet_name='data-services', index=False)

    # Hide data sheets
    writer.sheets['data-beds'].sheet_state = 'hidden'
    writer.sheets['data-nights'].sheet_state = 'hidden'
    writer.sheets['data-rent'].sheet_state = 'hidden'
    writer.sheets['data-services'].sheet_state = 'hidden'

    # Disconnect
    logger.info('Report finished')
    dbClient.disconnect()

    # return
    return temp