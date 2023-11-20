# ###################################################
# Imports
# ###################################################

# System includes
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.formula.translate import Translator
from openpyxl.worksheet.datavalidation import DataValidation
from datetime import datetime
from io import BytesIO
import pandas as pd
import warnings
import json
import os

# Cotown
from library.services.utils import super_flatten

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Fill excel with JSON
# ###################################################

def fill_sheet(df, columns, sheet):

  # Validations
  if sheet.title.lower() == 'rooming':

    #IdType
    dvIdType = DataValidation(type='list', formula1='=Id_type!$B$3:$B$9999', allow_blank=True)
    dvIdType.showInputMessage = True
    dvIdType.showErrorMessage = True
    sheet.add_data_validation(dvIdType)

    # Gender
    dvGender = DataValidation(type='list', formula1='=Gender!$B$3:$B$9999', allow_blank=True)
    dvGender.showInputMessage = True
    dvGender.showErrorMessage = True
    sheet.add_data_validation(dvGender)

    # Country
    dvCountry = DataValidation(type='list', formula1='=Country!$B$3:$B$9999', allow_blank=True)
    dvCountry.showInputMessage = True
    dvCountry.showErrorMessage = True
    sheet.add_data_validation(dvCountry)

    # Language
    dvLanguage = DataValidation(type='list', formula1='=Language!$B$3:$B$9999', allow_blank=True)
    dvLanguage.showInputMessage = True
    dvLanguage.showErrorMessage = True
    sheet.add_data_validation(dvLanguage)

  # Select and sort columns
  df = df.reindex([item.split(':')[0] for item in columns], axis=1)

  # Copy formats & styles from first data row
  styles = []
  format = []
  start = sheet.max_row
  for c in range(0, df.shape[1]):
    cell = sheet.cell(row=start, column=c+1)
    styles.append(cell._style)
    format.append(cell.value)

  # Write data
  for r, row in enumerate(dataframe_to_rows(df, index=False, header=False), 2):
    for c in range(0, df.shape[1]):

      # Get cell
      cell = sheet.cell(row = r + start - 2, column = c + 1)

      # Test validation
      if sheet.title.lower() == 'rooming':
        if columns[c] == 'Id_type.Name':
          dvIdType.add(cell)
        if columns[c] == 'Gender.Name':
          dvGender.add(cell)
        if columns[c] == 'Country.Name' or columns[c] == 'Nationality.Name' or columns[c] == 'Origin.Name':
          dvCountry.add(cell)
        if columns[c] == 'Language.Name':
          dvLanguage.add(cell)

      # Copy style
      cell._style = styles[c]

      # List of dicts
      if isinstance(row[c], list):
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
        # Format
        if format[c] == 'date':
          try:
            cell.value = datetime.strptime(row[c][:10], '%Y-%m-%d')
          except Exception as e:
            cell.value = row[c]
        elif format[c] == 'datetime':
          try:
            cell.value = datetime.strptime(row[c], '%Y-%m-%dT%H:%M:%S')
          except Exception as e:
            cell.value = row[c]
        elif format[c] is not None:
          t = Translator(format[c], 'A1')
          cell.value = t.translate_formula(row_delta = r - 2)
        else:
          cell.value = row[c]

  #http://localhost:5000/api/v1/export/rooming?id=1


# ###################################################
# Export graphql to excel
# ###################################################

def do_export_to_excel(apiClient, dbClient, name, variables=None):

  # Process variables (convert lists to tuple, for SQL WHERE IN)
  for var in variables:
    if isinstance(variables[var], str):
      if ',' in variables[var]:
        variables[var] = tuple(variables[var].split(','))
 
  # Get template
  fi = open('templates/report/' + name + '.xlsx', 'rb')
  template = BytesIO(fi.read())

  #http://localhost:5000/api/v1/export/rooming?id=1

  # Open template
  warnings.simplefilter(action='ignore', category=UserWarning)
  wb = load_workbook(filename=BytesIO(template.read()))
  for sheet in wb.sheetnames:

    # Querys
    query = None
    sql = None

    # Get graphQL query
    file = 'templates/report/' + name + '.' + sheet.lower() + '.graphql'
    if os.path.exists(file):   
      fi = open(file, 'r')
      query = fi.read()
      fi.close()

    # Get SQL query
    file = 'templates/report/' + name + '.' + sheet.lower() + '.sql'
    if os.path.exists(file):
      fi = open(file, 'r')
      sql = fi.read()
      fi.close()

    # Get columns
    file = 'templates/report/' + name + '.' + sheet.lower() + '.json'
    if os.path.exists(file):
      fi = open(file, 'r')
      columns = json.load(fi)
      fi.close()

    # Get graphQL data
    if query:
      result = apiClient.call(query, variables)
      data = result[next(iter(result.keys()))]
      df = pd.DataFrame([super_flatten(d) for d in data])
      fill_sheet(df, columns, wb[sheet])

    # Get SQL data
    if sql:
      try:
        dbClient.connect()
        dbClient.select(sql, variables)
        desc = [desc[0] for desc in dbClient.sel.description]
        data = dbClient.fetchall()
      except Exception as e:
        logging.error(e)
        dbClient.rollback()
        dbClient.disconnect()
        return
      dbClient.disconnect()
      df = pd.DataFrame(data, columns=desc)
      fill_sheet(df, columns, wb[sheet])

  # Save
  virtual_workbook = BytesIO()
  wb.save(virtual_workbook)
  virtual_workbook.seek(0)
  return virtual_workbook