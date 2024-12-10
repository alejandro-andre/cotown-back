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


def to_int(x):
  try:
    return int(x)
  except:
    return 0
  

def to_float(x):
  try:
    return float(x)
  except:
    return 0.0


def forecast(apiClient):

  # Log
  logger.info('Retrieving forecast...')

  # CSV header
  c = 0
  forecast_result = '"id","doc_id","doc_type","booking","date","provider","customer","resource","product","amount","rate","income_type","data_type","stay_length","discount_type"\n' 
  occupancy_result = '"id","data_type","resource","date","beds","beds_c","available","occupied","sold","occupied_t","sold_t"\n'

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

        # Data
        mgmt_fee  = to_float(row[ 2].value)
        beds      = to_float(row[ 3].value)
        beds_c    = to_float(row[ 4].value)
        beds_ad   = to_float(row[ 5].value)
        beds_st   = to_float(row[ 6].value)
        sold      = to_float(row[ 8].value)
        rent_l    = to_float(row[22].value)
        rent_m    = to_float(row[23].value)
        rent_s    = to_float(row[24].value)
        rent_g    = to_float(row[25].value)
        rent_tot  = to_float(row[26].value)
        srvs      = to_float(row[27].value) + to_float(row[28].value)
        bfee      = to_float(row[29].value)
        occ_stab  = to_float(row[37].value)
        rent_l_ad = rent_l * beds_ad / beds_c if beds_c else 0
        rent_m_ad = rent_m * beds_ad / beds_c if beds_c else 0
        rent_s_ad = rent_s * beds_ad / beds_c if beds_c else 0
        rent_g_ad = rent_g * beds_ad / beds_c if beds_c else 0
        mfee      = round((rent_tot + srvs / 1.21) * mgmt_fee, 2)

        # Forecast
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
        line = ['FBF' + str(c), '-', '-', '(forecast)', month, '', '', row[1].value, '1Gship fee', bfee, bfee, 'B2X', 'Forecast', '', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['FMF' + str(c), '-', '-', '(forecast)', month, '', '', row[1].value, 'Management fee', mfee, mfee, 'B2X', 'Forecast', '', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'

        # Forecast ajusted
        line = ['ARL' + str(c), '-', '-', '(forecast adjusted)', month, '', '', row[1].value, 'Monthly rent', rent_l_ad, rent_l_ad, 'B2X', 'Forecast adjusted', 'LONG', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['ARM' + str(c), '-', '-', '(forecast adjusted)', month, '', '', row[1].value, 'Monthly rent', rent_m_ad, rent_m_ad, 'B2X', 'Forecast adjusted', 'MEDIUM', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['ARS' + str(c), '-', '-', '(forecast adjusted)', month, '', '', row[1].value, 'Monthly rent', rent_s_ad, rent_s_ad, 'B2X', 'Forecast adjusted', 'SHORT', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['ARG' + str(c), '-', '-', '(forecast adjusted)', month, '', '', row[1].value, 'Monthly rent', rent_g_ad, rent_g_ad, 'B2X', 'Forecast adjusted', 'GROUP', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'

        # Stabilised
        rent = row[38].value or 0
        line = ['SIX' + str(c), '-', '-', '(stabilised)', month, '', '', row[1].value, 'Monthly rent', rent, rent, 'B2X', 'Stabilised', '', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'

        # Occupancy forecast
        if beds > 0:
          line = ['FOC' + str(c), 'Forecast', row[1].value, month, beds, beds_c, days * beds, days * sold, days * sold, 0, 0]
          occupancy_result += ','.join([f'"{e}"' for e in line]) + '\n'
          line = ['SOC' + str(c), 'Stabilised', row[1].value, month, beds_st, beds_st, days * beds_st, days * beds_st * occ_stab, days * beds_st * occ_stab, 0, 0]
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