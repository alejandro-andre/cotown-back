# ###################################################
# Imports
# ###################################################

from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.formula.translate import Translator
from io import BytesIO
import pandas as pd
import json

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Export graphql to excel
# ###################################################

def query_to_excel(apiClient, name, variables=None):

  # Get template
  fi = open('templates/report/' + name + '.xlsx', 'rb')
  template = BytesIO(fi.read())
  
  # Open template
  wb = load_workbook(filename=BytesIO(template.read()))
  for sheet in wb.sheetnames:

    # Get query
    fi = open('templates/report/' + sheet.lower() + '.graphql', 'r')
    query = fi.read()
    fi.close()

    # Get columns
    fi = open('templates/report/' + sheet.lower() + '.json', 'r')
    columns = json.load(fi)
    fi.close()

    # Call graphQL endpoint
    data = apiClient.call(query, variables)

    # Create dataframe
    df = pd.json_normalize(data[next(iter(data.keys()))])

    # Select and sort columns
    df = df.reindex([item.split(':')[0] for item in columns], axis=1)

    # Copy styles from first data row
    styles = []
    start = 3
    for c in range(0, df.shape[1]):
      cell = wb[sheet].cell(row=start, column=c+1)
      styles.append(cell._style)

    # Write data
    for r, row in enumerate(dataframe_to_rows(df, index=False, header=False), 2):
      for c in range(0, df.shape[1]):

        # Get cell
        cell = wb[sheet].cell(row = r + start - 2, column = c + 1)

        # Copy style
        cell._style = styles[c]

        # Blank column, skip
        if columns[c] == '':
          continue

        # Formula
        elif columns[c][0] == '=':
          t = Translator(columns[c], 'A1')
          cell.value = t.translate_formula(row_delta = r - 2)

        # List of dicts
        elif isinstance(row[c], list):
          try:
            values = []
            for item in row[c]:
              for key in columns[c].split(':')[1:]:
                item = item[key]
              values.append(str(item))
            cell.value = ','.join(values)
          except:
            cell.value = '[ERROR]'

        # Simple value
        else:
          cell.value = row[c]

  # Save
  virtual_workbook = BytesIO()
  wb.save(virtual_workbook)
  virtual_workbook.seek(0)
  return virtual_workbook


# ###################################################
# Export json data to excel
# ###################################################

def json_to_excel(json, name):

  pass