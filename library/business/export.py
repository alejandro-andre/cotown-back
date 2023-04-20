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
# Export to excel
# ###################################################

def export_to_excel(apiClient, name, variables=None):

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
        df = df.reindex(columns, axis=1)

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
                if columns[c][0] == '=':
                    t = Translator(columns[c], 'A1')
                    cell.value = t.translate_formula(row_delta = r - 2)

                # Value
                else:
                    cell.value = row[c]

    # Save
    virtual_workbook = BytesIO()
    wb.save(virtual_workbook)
    virtual_workbook.seek(0)
    return virtual_workbook