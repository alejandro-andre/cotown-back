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
  occupancy_result = '"id","data_type","resource","date","beds","available","occupied","sold"\n'

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

        # Income forecast
        line = ['FL' + str(c), '-', '-', '', month, '', '', row[1].value, 'Monthly rent', row[22].value, row[22].value, 'B2X', 'Forecast', 'LONG', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['FM' + str(c), '-', '-', '', month, '', '', row[1].value, 'Monthly rent', row[23].value, row[23].value, 'B2X', 'Forecast', 'MEDIUM', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['FS' + str(c), '-', '-', '', month, '', '', row[1].value, 'Monthly rent', row[24].value, row[24].value, 'B2X', 'Forecast', 'SHORT', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['FG' + str(c), '-', '-', '', month, '', '', row[1].value, 'Monthly rent', row[25].value, row[25].value, 'B2X', 'Forecast', 'GROUP', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'

        # Income stabilised
        line = ['ST' + str(c), '-', '-', '', month, '', '', row[1].value, 'Monthly rent', row[36].value, row[36].value, 'B2X', 'Stabilised', '', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'

        # Income UW
        line = ['UW' + str(c), '-', '-', '', month, '', '', row[1].value, 'Monthly rent', row[39].value, row[39].value, 'B2X', 'UW', '', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'

        # Occupancy forecast
        line = ['OF' + str(c), 'forecast', row[1].value, month, row[3].value, days * row[3].value, days * row[8].value, days * row[8].value]
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
