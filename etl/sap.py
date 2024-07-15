# ###################################################
# Imports
# ###################################################

import requests
from requests.auth import HTTPBasicAuth

import re
import json
from datetime import datetime, timezone


# ###################################################
# Connection params
# ###################################################

# URL
url = 'https://my429724.businessbydesign.cloud.sap/sap/byd/odata/ana_businessanalytics_analytics.svc/RPFINGLAU02_Q0001QueryResults'

# Query string
params = {
'$select': "CFIX_ASSET_UUID,TFIX_ASSET_UUID,CACC_DOC_UUID,CPROFITCTR_UUID,TPROFITCTR_UUID,CCOST_CTR_UUID,TCOST_CTR_UUID,CCREATION_DATE,CGLACCT,TGLACCT,CFISCYEAR,CCOMPANY_UUID,TCOMPANY_UUID,CPOSTING_DATE,CDOC_DATE,COFF_BUSPARTNER,COEDREF_F_ID,COEOREF_F_ID,CFISCPER,CACC_DOC_IT_UUID,CPRODUCT_UUID,TPRODUCT_UUID,COEDPARTNER,CBUS_PART_UUID,TBUS_PART_UUID,CNOTE_HD,CNOTE_IT,CACCDOCTYPE,KCDEBIT_CURRCOMP,KCCREDIT_CURRCOMP",
'$filter': "(PARA_SETOFBKS eq 'ES01' and PARA_COMPANY eq 'VDS0000001' and CCREATION_DATE ge datetime'2024-07-01T00:00:00')",
'$format': "json"
}

# Auth
username = 'lorumdesarrollo'
password = 'Vandor12345678912'


# ###################################################
# Utils
# ###################################################

def get_date(value):

    milliseconds = int(re.search(r'\d+', value).group())
    date = datetime.fromtimestamp(milliseconds / 1000.0, tz=timezone.utc)
    return date.strftime('%Y-%m-%d %H:%M:%S %Z')


# ###################################################
# Get data
# ###################################################

def main():

    # Request
    response = requests.get(url, params=params, auth=HTTPBasicAuth(username, password))
    if response.status_code != 200:
        print(response.status_code)
        return

    # Get data
    data = response.json()
    if not data:
        return
    
    # Get records
    results = data['d']['results']
    for row in results[:1]:
        for col in row:
            if col != '__metadata':
                print(col, ':', row[col])
        #print(row['CCREATION_DATE'], get_date(row['CCREATION_DATE']))


# ###################################################
# Start
# ###################################################

if __name__ == '__main__':
    main()