# ###################################################
# Imports
# ###################################################

# System includes
import openpyxl

# Logging
import logging
logger = logging.getLogger('COTOWN')


def forecast():

  # Log
  logger.info('Calculating forecast...')

  workbook = openpyxl.load_workbook('csv/income_forecast.xlsx')

  result = '''"id","doc_id","doc_type","booking","date","provider","customer","resource","product","amount","rate","income_type","data_type","stay_length"\n''' 
  for name in ('Forecast', 'Stabilised'):
    sheet = workbook[name]
    for row in sheet.iter_rows(values_only=True):
        month = 1
        for cel in row[1:]:
            line = [
                'C' + name[0] + row[0] + '2024' + str(month).zfill(2),
                '-', '-', '', '2024-' + str(month).zfill(2) + '-01',
                '', '', row[0], 'Monthly rent', round(cel, 2), round(cel, 2), 'B2X', name, ""
            ]
            result += ','.join([f'"{e}"' for e in line]) + '\n'
            month += 1

  workbook.close()

  with open('csv/income_forecast.csv', 'w') as f:
    f.write(result)

  # Log
  logger.info('Done')