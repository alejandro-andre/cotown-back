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
  forecast_result = '"id","doc_id","doc_type","booking","date","provider","customer","resource","product","amount","rate","data_type","stay_length","discount_type"\n' 
  occupancy_result = '"id","data_type","resource","date","occupied","sold","occupied_t","sold_t","booking","stay_length"\n'
  beds_result = '"id","data_type","resource","date","beds","beds_c","beds_cnv","beds_pot","beds_pre","beds_cap","available","convertible"\n'

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
        beds_pot  = to_float(row[ 7].value)
        sold      = to_float(row[ 9].value)
        rent_l    = to_float(row[23].value)
        rent_m    = to_float(row[24].value)
        rent_s    = to_float(row[25].value)
        rent_g    = to_float(row[26].value)
        rent_tot  = to_float(row[27].value)
        srvs      = to_float(row[28].value) + to_float(row[29].value)
        bfee      = to_float(row[30].value)
        occ_stab  = to_float(row[38].value)
        mpr       = to_float(row[39].value)
        mpr_st    = to_float(row[40].value)
        mpr_pot   = to_float(row[41].value)
        rent_l_ad = (rent_l * beds_ad / beds_c) if beds_c else 0
        rent_m_ad = (rent_m * beds_ad / beds_c) if beds_c else 0
        rent_s_ad = (rent_s * beds_ad / beds_c) if beds_c else 0
        rent_g_ad = (rent_g * beds_ad / beds_c) if beds_c else 0
        mfee      = round((rent_tot + srvs / 1.21) * mgmt_fee, 2)

        # Forecast
        line = ['FRL' + str(c), '-', '-', '(forecast)', month, '', '', row[1].value, 'Monthly rent', rent_l, rent_l, 'Forecast', 'LONG', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['FRM' + str(c), '-', '-', '(forecast)', month, '', '', row[1].value, 'Monthly rent', rent_m, rent_m, 'Forecast', 'MEDIUM', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['FRS' + str(c), '-', '-', '(forecast)', month, '', '', row[1].value, 'Monthly rent', rent_s, rent_s, 'Forecast', 'SHORT', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['FRG' + str(c), '-', '-', '(forecast)', month, '', '', row[1].value, 'Monthly rent', rent_g, rent_g, 'Forecast', 'GROUP', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['FSV' + str(c), '-', '-', '(forecast)', month, '', '', row[1].value, 'Monthly services', srvs, srvs, 'Forecast', '', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['FBF' + str(c), '-', '-', '(forecast)', month, '', '', row[1].value, 'Membership fee', bfee, bfee, 'Forecast', '', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['FMF' + str(c), '-', '-', '(forecast)', month, '', '', row[1].value, 'Management fee', mfee, mfee, 'Forecast', '', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'

        # Forecast ajusted
        line = ['ARL' + str(c), '-', '-', '(forecast adjusted)', month, '', '', row[1].value, 'Monthly rent', rent_l_ad, rent_l_ad, 'Forecast adjusted', 'LONG', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['ARM' + str(c), '-', '-', '(forecast adjusted)', month, '', '', row[1].value, 'Monthly rent', rent_m_ad, rent_m_ad, 'Forecast adjusted', 'MEDIUM', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['ARS' + str(c), '-', '-', '(forecast adjusted)', month, '', '', row[1].value, 'Monthly rent', rent_s_ad, rent_s_ad, 'Forecast adjusted', 'SHORT', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['ARG' + str(c), '-', '-', '(forecast adjusted)', month, '', '', row[1].value, 'Monthly rent', rent_g_ad, rent_g_ad, 'Forecast adjusted', 'GROUP', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'

        # MPR
        line = ['MPA' + str(c), '-', '-', '(MPR available)', month, '', '', row[1].value, 'Monthly rent', mpr, mpr, 'MPR Available', '', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['MPC' + str(c), '-', '-', '(MPR convertible)', month, '', '', row[1].value, 'Monthly rent', mpr_st, mpr_st, 'MPR Convertible', '', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['MPP' + str(c), '-', '-', '(MPR potential)', month, '', '', row[1].value, 'Monthly rent', mpr_pot, mpr_pot, 'MPR Potential', '', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'

        # Stabilised
        line = ['SPA' + str(c), '-', '-', '(Stabilised available)', month, '', '', row[1].value, 'Monthly rent', mpr * occ_stab, mpr * occ_stab, 'Stabilised Available', '', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['SPC' + str(c), '-', '-', '(Stabilised convertible)', month, '', '', row[1].value, 'Monthly rent', mpr_st * occ_stab, mpr_st * occ_stab, 'Stabilised Convertible', '', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'
        line = ['SPP' + str(c), '-', '-', '(Stabilised potential)', month, '', '', row[1].value, 'Monthly rent', mpr_pot * occ_stab, mpr_pot * occ_stab, 'Stabilised Potential', '', '' ]
        forecast_result += ','.join([f'"{e}"' for e in line]) + '\n'

        # Occupancy forecast
        if beds > 0:
          line = ['FOC' + str(c), 'Forecast', row[1].value, month, days * sold, days * sold, 0, 0, '', '']
          occupancy_result += ','.join([f'"{e}"' for e in line]) + '\n'
          line = ['FOC' + str(c), 'Forecast', row[1].value, month, beds, beds_c, beds_st, beds_pot, 0, 0, days * beds, '']
          beds_result += ','.join([f'"{e}"' for e in line]) + '\n'
        if beds_st > 0:
          line = ['SOC' + str(c), 'Stabilised', row[1].value, month, days * beds_st * occ_stab, days * beds_st * occ_stab, 0, 0, '', '']
          occupancy_result += ','.join([f'"{e}"' for e in line]) + '\n'
          line = ['SOC' + str(c), 'Stabilised', row[1].value, month, beds_st, beds_st, beds_st, beds_pot, 0, 0, days * beds_st, '']
          beds_result += ','.join([f'"{e}"' for e in line]) + '\n'

    # Close worksheet
    workbook.close()

  # Save all results to CSV
  with open('csv/income_forecast.csv', 'w') as f:
    f.write(forecast_result)

  # Save all results to CSV
  with open('csv/occupancy_forecast.csv', 'w') as f:
    f.write(occupancy_result)
  with open('csv/beds_forecast.csv', 'w') as f:
    f.write(beds_result)

  # Log
  logger.info('Done')