# ###################################################
# Imports
# ###################################################

import re
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timezone
from openpyxl import load_workbook

import pandas as pd
import csv

from library.services.config import settings

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Utils
# ###################################################

def get_excel_date(value):

  date = datetime.strptime(value, '%d.%m.%Y')
  return date.strftime('%Y-%m-%d')


def get_excel_datetime(value):

  date = datetime.strptime(value, '%d.%m.%Y')
  return date.strftime('%Y-%m-%dT%H:%M:%S')


def get_sap_date(value):

  milliseconds = int(re.search(r'\d+', value).group())
  date = datetime.fromtimestamp(milliseconds / 1000.0, tz=timezone.utc)
  return date.strftime('%Y-%m-%d')

def get_sap_datetime(value):

  milliseconds = int(re.search(r'\d+', value).group())
  date = datetime.fromtimestamp(milliseconds / 1000.0, tz=timezone.utc)
  return date.strftime('%Y-%m-%dT%H:%M:%S')



# ###################################################
# Get GL data from Excel
# ###################################################

def glExcel(file, year):

  # Log
  logger.info('Retrieving data from Excel (' + file + ')...')

  # Read XLSX 
  df = pd.read_excel(
    'csv/' + file + '.xlsx', 
    skiprows=13, 
    skipfooter=1,
    names=['_','cglacct','tglacct','tproduct_uuid','tproduct_type','cacc_doc_uuid','cfiscper','cdoc_date','cposting_date','ccreation_date','cnote_hd','cnote_it','cprofitctr_uuid','tprofitctr_uuid','cbus_part_uuid','tbus_part_uuid','ccost_ctr_uuid','tcost_ctr_uuid','coedpartner','coedref_f_id','coff_glacct','toff_glacct','cfix_asset_uuid','tfix_asset_uuid','cfiscyear','cacc_doc_it_uuid','kcdebit_currcomp','kccredit_currcomp','kcbalance_currcomp']
  )

  # Dates
  df['ccreation_date'] = df['ccreation_date'].apply(lambda x: get_excel_datetime(x))
  df['cposting_date'] = df['cposting_date'].apply(lambda x: get_excel_date(x))
  df['cdoc_date'] = df['cdoc_date'].apply(lambda x: get_excel_date(x))
  df['ccreation_date'] = pd.to_datetime(df['ccreation_date'])
  df['cposting_date'] = pd.to_datetime(df['cposting_date'])
  df['cdoc_date'] = pd.to_datetime(df['cdoc_date'])

  # Cleanup
  df = df.reset_index()
  df = df.drop(columns=['_'])
  df = df.drop(columns=['index'])

  # Write CSV
  logger.info('Retrieved ' + str(len(df)) + ' records...')
  df.to_csv('csv/' + file + '.csv', index=False, quoting=csv.QUOTE_MINIMAL)



# ###################################################
# Get GL data from SAP
# ###################################################

def glSAP(date, bks, company, file):

  params = {
      '$select': 'CFISCYEAR,CFISCPER,CGLACCT,TGLACCT,TPRODUCT_UUID,TPRODUCT_TYPE,CACC_DOC_UUID,CACC_DOC_IT_UUID,CDOC_DATE,CPOSTING_DATE,CCREATION_DATE,CNOTE_HD,CNOTE_IT,CPROFITCTR_UUID,TPROFITCTR_UUID,CBUS_PART_UUID,TBUS_PART_UUID,CCOST_CTR_UUID,TCOST_CTR_UUID,COEDPARTNER,COEDREF_F_ID,COFF_GLACCT,TOFF_GLACCT,CFIX_ASSET_UUID,TFIX_ASSET_UUID,KCDEBIT_CURRCOMP,KCCREDIT_CURRCOMP,KCBALANCE_CURRCOMP',
      '$filter': '(PARA_SETOFBKS eq \'' + bks + '\' and PARA_COMPANY eq \'' + company + '\' and CCREATION_DATE ge datetime\'' + date + 'T00:00:00\')',
      '$orderby': 'CACC_DOC_UUID,CACC_DOC_IT_UUID',
      '$format': 'json',
      '$top': 999999
  }

  # Request
  logger.info('Retrieving data from SAP...')
  response = requests.get(settings.SAPURL_GL, params=params, auth=HTTPBasicAuth(settings.SAPUSER, settings.SAPPASS))
  if response.status_code != 200:
      logger.error(response.status_code)
      logger.error(response.text)
      return

  # Get data
  data = response.json()
  if not data:
      return
  
  # Results
  results = data['d']['results']
  logger.info('Retrieved ' + str(len(results)) + ' records...')

  # Dataframe
  df = pd.DataFrame(results)
  df.columns = df.columns.str.lower()

  # Drop unused columns
  df = df.drop(['__metadata'], axis=1)

  # Remove 'null'
  df.replace('null', None, inplace=True)

  # Convert dates
  df['ccreation_date'] = df['ccreation_date'].apply(lambda x: get_sap_datetime(x))
  df['cposting_date'] = df['cposting_date'].apply(lambda x: get_sap_date(x))
  df['cdoc_date'] = df['cdoc_date'].apply(lambda x: get_sap_date(x))
  df['ccreation_date'] = pd.to_datetime(df['ccreation_date'])
  df['cposting_date'] = pd.to_datetime(df['cposting_date'])
  df['cdoc_date'] = pd.to_datetime(df['cdoc_date'])

  # Convert numbers
  df[['kccredit_currcomp', 'kcdebit_currcomp']] = df[['kccredit_currcomp', 'kcdebit_currcomp']].fillna(0)
  df['kccredit_currcomp'] = df['kccredit_currcomp'].astype(float)
  df['kcdebit_currcomp'] = df['kcdebit_currcomp'].astype(float)

  # Save CSV
  year = results[0]['CFISCYEAR']
  period = results[0]['CFISCPER']
  df.to_csv('csv/' + company + '-' + str(year) + '-' + str(period).zfill(2) + '.csv', index=False, quoting=csv.QUOTE_MINIMAL)