# ###################################################
# Imports
# ###################################################

import pandas as pd
import csv

# Logging
import logging
logger = logging.getLogger('COTOWN')


def convert_date_format(date_str):

  if pd.isna(date_str):
    return date_str
  parts = date_str.split('.')
  return f'{parts[2]}/{parts[1]}/{parts[0]}'


def gl(file):

  # Log
  logger.info('Formatting general ledger...')

  # Read XLSX 
  df = pd.read_excel(file + '.xlsx')

  # Changes
  df['debit'] = df['debit'].fillna(0)
  df['credit'] = df['credit'].fillna(0)
  df['date'] = df['date'].apply(convert_date_format)
  df['original_date'] = df['original_date'].apply(convert_date_format)

  # Write CSV
  df.to_csv(file + '.csv', index=False, quoting=csv.QUOTE_ALL)