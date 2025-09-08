# ###################################################
# Imports
# ###################################################

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Utils
# ###################################################

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


# ###################################################
# Load resources
# ###################################################

def load_forecast(dbClient, con, data):

  # Return values
  n_ok = n_ko = 0
  log = ''

  # Header
  header = list(map(lambda cell: cell.value, data[2]))

  # Loop thru all rows skipping two first rows
  for irow, row in enumerate(data.iter_rows(min_row=3)):
    # Skip empty rows
    if all((cell.value is None or cell.value == '') for cell in row):
      continue

    # Process
    try:

      # Empty record
      record = {}
      extras = []

      # Ok
      ok = True

      # Loop thru each column
      for icol, cell in enumerate(row):

        # Column
        column = header[icol]

        # Discard some columns
        if column is None or isinstance(column, int):
          pass

        # Resource.Code
        elif column == 'Resource.Code':
          id = None
          if cell.value is not None and cell.value != '':
            cur = dbClient.execute(con, 'SELECT id FROM "Resource"."Resource" WHERE "Code"=%s', [cell.value])
            aux = cur.fetchone()
            cur.close()
            if aux is None:
              log += 'Fila: ' + str(irow+3).zfill(4) + '. Recurso "' + str(cell.value) + '" no encontrado\n'
              ok = False
            else: 
              id = aux['id']
          record['Resource_id'] = id

        # Copy cells
        else:
          record[column] = cell.value

      # Fix values
      record['Occupancy']      = to_float(record['Occupancy']) * 100
      record['Rent_long']      = to_float(record['Rent_long'])
      record['Rent_short']     = to_float(record['Rent_short'])
      record['Rent_medium']    = to_float(record['Rent_medium'])
      record['Rent_group']     = to_float(record['Rent_group'])
      record['Pct_short']      = to_float(record['Pct_short']) * 100
      record['Pct_medium']     = to_float(record['Pct_medium']) * 100
      record['Pct_long']       = to_float(record['Pct_long']) * 100
      record['Discount']       = to_float(record['Discount']) * 100
      record['Services']       = to_float(record['Services'])
      record['Final_cleaning'] = to_float(record['Final_cleaning'])
      record['Booking_fee']    = to_float(record['Booking_fee'])
      record['Reinvoices']     = to_float(record['Reinvoices'])

      # Insert record
      fields = list(map(lambda key: '"' + key + '"', record.keys()))
      update = list(map(lambda key: '"'+ key + '"=EXCLUDED."' + key + '"', record.keys()))
      values = [record[field] for field in record.keys()]
      markers = ['%s'] * len(record.keys())
      sql = 'INSERT INTO "Resource"."Resource_forecast" ({}) VALUES ({}) ON CONFLICT ("Resource_id", "Date_price") DO UPDATE SET {} RETURNING ID'.format(','.join(fields), ','.join(markers), ','.join(update))
      cur = dbClient.execute(con, sql, values)
      id = cur.fetchone()[0]

    # Error
    except Exception as error:
      logger.error(error)
      con.rollback()
      log += 'Fila: ' + str(irow+3).zfill(4) + '. Contiene datos erróneos.\n'
      e = str(error)
      if (e.startswith('!!!')):
        log += e.split('!!!')[2] + '\n'
      else:
        log += e + '\n'
      ok = False

    # Count oks and errors
    if ok:
      n_ok += 1
    else:
      n_ko += 1

  # Rollback?
  if n_ko > 0:
    con.rollback()
    log += 'Analizados ' + str(n_ok) + ' registro(s) correctamente\n'
    log += 'Analizados ' + str(n_ko) + ' registro(s) con errores\n'
    log += 'No se han cargado datos\n'
  else:
    con.commit()
    log += 'Cargados ' + str(n_ok) + ' registro(s) correctamente\n'
   
  # Return
  return (n_ko == 0), log  