# ###################################################
# Imports
# ###################################################

import re
import requests
from requests.auth import HTTPBasicAuth
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
        '$select': "CCREATION_DATE,CGLACCT,TGLACCT,CPOSTING_DATE,CACC_DOC_UUID,CACC_DOC_IT_UUID,TACCDOCTYPE,CPROFITCTR_UUID,TPROFITCTR_UUID,CCOST_CTR_UUID,TCOST_CTR_UUID,CDOC_DATE,TPRODUCT_UUID,TPRODUCT_TYPE,COEDPARTNER,CBUS_PART_UUID,TBUS_PART_UUID,CNOTE_HD,CNOTE_IT,KCDEBIT_CURRCOMP,KCCREDIT_CURRCOMP",
        '$filter': "(PARA_SETOFBKS eq '" + bks + "' and PARA_COMPANY eq '" + company + "' and CCREATION_DATE ge datetime'" + date + "T00:00:00')",
        '$orderby': "CACC_DOC_UUID,CACC_DOC_IT_UUID",
        '$format': "json",
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

    # Remove "null"
    df.replace('null', None, inplace=True)

    # Convert dates
    df['ccreation_date'] = df['ccreation_date'].apply(lambda x: get_date(x))
    df['cdoc_date'] = df['cdoc_date'].apply(lambda x: get_date(x))
    df['cposting_date'] = df['cposting_date'].apply(lambda x: get_date(x))

    # Convert numbers
    df[['kccredit_currcomp', 'kcdebit_currcomp']] = df[['kccredit_currcomp', 'kcdebit_currcomp']].fillna(0)
    df['kccredit_currcomp'] = df['kccredit_currcomp'].astype(float)
    df['kcdebit_currcomp'] = df['kcdebit_currcomp'].astype(float)

    # Save CSV
    df.to_csv('csv/' + file + '.csv', index=False, quoting=csv.QUOTE_MINIMAL)