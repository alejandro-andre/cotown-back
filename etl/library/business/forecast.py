# ###################################################
# Imports
# ###################################################

# System includes
from io import BytesIO
import openpyxl

# Logging
import logging
logger = logging.getLogger('COTOWN')


def forecast(apiClient):

  # Log
  logger.info('Retrieving forecast...')

  # CSV header
  result = '"id","doc_id","doc_type","booking","date","provider","customer","resource","product","amount","rate","income_type","data_type","stay_length","discount_type"\n' 

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
        month = str(row[0].value)[:10]

        # Forecast
        line = ['XXXX', '-', '-', '', month, '', '', row[1].value, 'Monthly rent', row[22].value, row[22].value, 'B2X', 'Forecast', 'LONG', '' ]
        result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['XXXX', '-', '-', '', month, '', '', row[1].value, 'Monthly rent', row[23].value, row[23].value, 'B2X', 'Forecast', 'MEDIUM', '' ]
        result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['XXXX', '-', '-', '', month, '', '', row[1].value, 'Monthly rent', row[24].value, row[24].value, 'B2X', 'Forecast', 'SHORT', '' ]
        result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['XXXX', '-', '-', '', month, '', '', row[1].value, 'Monthly rent', row[25].value, row[25].value, 'B2X', 'Forecast', 'GROUP', '' ]
        result += ','.join([f'"{e}"' for e in line]) + '\n'

        # Stabilised
        line = ['XXXX', '-', '-', '', month, '', '', row[1].value, 'Monthly rent', row[36].value, row[36].value, 'B2X', 'Stabilised', '', '' ]
        result += ','.join([f'"{e}"' for e in line]) + '\n'

        # UW
        line = ['XXXX', '-', '-', '', month, '', '', row[1].value, 'Monthly rent', row[39].value, row[39].value, 'B2X', 'UW', '', '' ]
        result += ','.join([f'"{e}"' for e in line]) + '\n'

    # Close worksheet
    workbook.close()

  # Save all results to CSV
  with open('csv/income_forecast.csv', 'w') as f:
    f.write(result)

  # Log
  logger.info('Done')