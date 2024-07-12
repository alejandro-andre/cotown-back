# ###################################################
# Imports
# ###################################################

# System includes
from io import BytesIO
import calendar
import openpyxl

# Logging
import logging
logger = logging.getLogger('COTOWN')


def forecast(apiClient):

  # Log
  logger.info('Retrieving forecast...')

  # CSV header
  c = 0
  forecast_result = '"id","doc_id","doc_type","booking","date","provider","customer","resource","product","amount","rate","income_type","data_type","stay_length","discount_type"\n' 
  occupancy_result = '"id","data_type","resource","date","beds","available","occupied","sold","occupied_t","sold_t"\n'

  # Get files
  files = apiClient.call('{ data: Admin_FilesList ( where: { Name: { LIKE: "Forecast%" } } ) { id File { name } } }')
  for file in files['data']:

    # Retrieve file
    data = apiClient.getFile(file['id'], 'Admin/Files')
    bytes = BytesIO(data.content)

    # Log
    logger.info('Calculating forecast from "' + file['File']['name'] + '"...')

    # Open XLSX and get each sheet
    workbook = openpyxl.load_workbook(bytes, data_only=True)
    for name in workbook.sheetnames:
    
      # Process sheet
      sheet = workbook[name]
      for row in sheet.iter_rows(min_row=5):
        c += 1
        month = str(row[0].value)[:10]
        days = calendar.monthrange(int(month[:4]), int(month[5:7]))[1]

        # Forecast
        rent_l = row[22].value or 0
        rent_m = row[23].value or 0
        rent_s = row[24].value or 0
        rent_g = row[25].value or 0
        srvs   = row[27].value or 0
        bfee   = row[28].value or 0
        mfee   = round((float(row[26].value or 0) + float(row[27].value or 0) / 1.21) * float(row[2].value or 0), 2)
        line = ['FRL' + str(c), '-', '-', '(forecast)', month, '', '', row[1].value, 'Monthly rent', rent_l, rent_l, 'B2X', 'Forecast', 'LONG', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['FRM' + str(c), '-', '-', '(forecast)', month, '', '', row[1].value, 'Monthly rent', rent_m, rent_m, 'B2X', 'Forecast', 'MEDIUM', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['FRS' + str(c), '-', '-', '(forecast)', month, '', '', row[1].value, 'Monthly rent', rent_s, rent_s, 'B2X', 'Forecast', 'SHORT', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['FRG' + str(c), '-', '-', '(forecast)', month, '', '', row[1].value, 'Monthly rent', rent_g, rent_g, 'B2X', 'Forecast', 'GROUP', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['FSV' + str(c), '-', '-', '(forecast)', month, '', '', row[1].value, 'Monthly services', srvs, srvs, 'B2X', 'Forecast', '', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['FBF' + str(c), '-', '-', '(forecast)', month, '', '', row[1].value, 'Membership fee', bfee, bfee, 'B2X', 'Forecast', '', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['FMF' + str(c), '-', '-', '(forecast)', month, '', '', row[1].value, 'Management fee', mfee, mfee, 'B2X', 'Forecast', '', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'

        # Stabilised
        rent = row[38].value or 0
        line = ['SIX' + str(c), '-', '-', '(stabilised)', month, '', '', row[1].value, 'Monthly rent', rent, rent, 'B2X', 'Stabilised', '', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'

        # UW
        rent = row[41].value or 0
        line = ['UIX' + str(c), '-', '-', '(uw)', month, '', '', row[1].value, 'Monthly rent', rent, rent, 'B2X', 'UW', '', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'

        #"id","data_type","resource","date","beds","available","occupied","sold"\n'''

        # Occupancy forecast
        beds     = row[3].value or 0 
        beds_uw  = row[6].value or 0
        sold     = row[8].value or 0
        occ_stab = row[36].value or 0
        occ_uw   = row[40].value or 0
        line = ['FOC' + str(c), 'Forecast', row[1].value, month, beds, days * beds, days * sold, days * sold, 0, 0]
        occupancy_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['SOC' + str(c), 'Stabilised', row[1].value, month, beds, days * beds, days * beds * occ_stab, days * beds * occ_stab, 0, 0]
        occupancy_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['UOC' + str(c), 'UW', row[1].value, month, beds_uw, days * beds_uw, days * beds_uw * occ_uw,  days * beds_uw * occ_uw, 0, 0]
        occupancy_result += ','.join([f'"{e}"' for e in line]) + '\n'

    # Close worksheet
    workbook.close()

  # Save all results to CSV
  with open('csv/income_forecast.csv', 'w') as f:
    f.write(forecast_result)

  # Save all results to CSV
  with open('csv/occupancy_forecast.csv', 'w') as f:
    f.write(occupancy_result)

  # Log
  logger.info('Done')
