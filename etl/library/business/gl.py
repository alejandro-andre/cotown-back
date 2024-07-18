# ###################################################
# Imports
# ###################################################

import requests
from requests.auth import HTTPBasicAuth

import re
from datetime import datetime, timezone

import pandas as pd
import csv

from library.services.config import settings

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Constants
# ###################################################

PAGESIZE = 25


# ###################################################
# Utils
# ###################################################

def get_date(value):

    milliseconds = int(re.search(r'\d+', value).group())
    date = datetime.fromtimestamp(milliseconds / 1000.0, tz=timezone.utc)
    return date.strftime('%Y-%m-%d')


# ###################################################
# Get GL data
# ###################################################

def gl(date, bks, company, file):

    params = {
        '$select': "CFIX_ASSET_UUID,TFIX_ASSET_UUID,CACC_DOC_UUID,CPROFITCTR_UUID,TPROFITCTR_UUID,CCOST_CTR_UUID,TCOST_CTR_UUID,CCREATION_DATE,CGLACCT,TGLACCT,CFISCYEAR,CCOMPANY_UUID,TCOMPANY_UUID,CPOSTING_DATE,CDOC_DATE,COFF_BUSPARTNER,COEDREF_F_ID,COEOREF_F_ID,CFISCPER,CACC_DOC_IT_UUID,CPRODUCT_UUID,TPRODUCT_UUID,COEDPARTNER,CBUS_PART_UUID,TBUS_PART_UUID,CNOTE_HD,CNOTE_IT,CACCDOCTYPE,KCDEBIT_CURRCOMP,KCCREDIT_CURRCOMP",
        '$filter': "(PARA_SETOFBKS eq '" + bks + "' and PARA_COMPANY eq '" + company + "' and CCREATION_DATE ge datetime'" + date + "T00:00:00')",
        '$orderby': "CACC_DOC_UUID",
        '$format': "json",
        '$top': 999999
    }

    # Request
    logger.info('Retrieving data from SAP...')
    response = requests.get(settings.SAPURL_GL, params=params, auth=HTTPBasicAuth(settings.SAPUSER, settings.SAPPASS))
    if response.status_code != 200:
        logger.error(response.status_code)
        return

    # Get data
    data = response.json()
    if not data:
        return
    
    # Results
    results = data['d']['results']
    logger.info('Loaded ' + str(len(results)) + ' records...')

    # Dataframe
    df = pd.DataFrame(results)

    # Drop unused columns
    df = df.drop(['__metadata'], axis=1)

    # Convert dates
    df['CCREATION_DATE'] = df['CCREATION_DATE'].apply(lambda x: get_date(x))
    df['CDOC_DATE'] = df['CDOC_DATE'].apply(lambda x: get_date(x))
    df['CDOC_DATE'] = df['CDOC_DATE'].apply(lambda x: get_date(x))
    df['CPOSTING_DATE'] = df['CPOSTING_DATE'].apply(lambda x: get_date(x))

    # Save CSV
    df.to_csv('csv/' + file + '.csv', index=False, quoting=csv.QUOTE_ALL)


# ###################################################
# Get mapping data
# ###################################################

def mapping(file):

  # Log
  logger.info('Formatting mapping...')

  # Read XLSX 
  df = pd.read_excel(file + '.xlsx')

  # Write CSV
  df.to_csv(file + '.csv', index=False, quoting=csv.QUOTE_ALL)