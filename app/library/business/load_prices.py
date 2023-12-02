# ###################################################
# Imports
# ###################################################

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Load prices
# ###################################################

def load_prices(dbClient, con, data):

  # Return values
  n_ok = n_ko = 0
  log = ''

  # Header
  header = list(map(lambda cell: cell.value, data[2]))

  # Loop thru all rows skipping two first rows
  for irow, row in enumerate(data.iter_rows(min_row=3)):
    try:

      # Empty record
      record = {}

      # Ok by default
      ok = True

      # Loop thru each column
      for icol, cell in enumerate(row):

        # Column
        column = header[icol]

        # Discard some columns
        if column is None or isinstance(column, int):
          pass

        # Building.Code
        elif column == 'Building.Code':
          cur = dbClient.execute(con, 'SELECT id FROM "Building"."Building" WHERE "Code"=%s', (cell.value,))
          aux = cur.fetchone()
          cur.close()
          if aux is None:
            log += 'Fila: ' + str(irow+3).zfill(4) + '. Edificio "' + str(cell.value) + '" no encontrado\n'
            ok = False
          else: 
            record['Building_id'] = aux['id']

        # Resource_flat_type.Code
        elif column == 'Flat_type.Code':
          id = None
          if cell.value is not None and cell.value != '':
            cur = dbClient.execute(con, 'SELECT id, "Name" FROM "Resource"."Resource_flat_type" WHERE "Code"=%s', (cell.value,))
            aux = cur.fetchone()
            cur.close()
            if aux is None:
              log += 'Fila: ' + str(irow+3).zfill(4) + '. Tipo de piso "' + str(cell.value) + '" no encontrado\n'
              ok = False
            else: 
              id = aux['id']
          record['Flat_type_id'] = id

        # Resource_place_type.Code
        elif column == 'Place_type.Code':
          id = None
          if cell.value is not None and cell.value != '':
            cur = dbClient.execute(con, 'SELECT id, "Name" FROM "Resource"."Resource_place_type" WHERE "Code"=%s', (cell.value,))
            aux = cur.fetch()
            cur.close()
            if aux is None:
              log += 'Fila: ' + str(irow+3).zfill(4) + '. Tipo de habitación/plaza "' + str(cell.value) + '" no encontrado\n'
              ok = False
            else: 
              id = aux['id']
          record['Place_type_id'] = id

        # Copy cells
        else:
          record[column] = cell.value

      # Resource type
      if record['Place_type_id'] is None:
        record['Resource_type'] = 'piso'
      else:
        record['Resource_type'] = 'habitacion'

      # Insert records
      fields = list(map(lambda key: '"' + key + '"', record.keys()))
      update = list(map(lambda key: '"'+ key + '"=EXCLUDED."' + key + '"', record.keys()))
      values = [record[field] for field in record.keys()]
      markers = ['%s'] * len(record.keys())
      sql = 'INSERT INTO "Billing"."Pricing_detail" ({}) VALUES ({}) ON CONFLICT ("Year","Building_id","Flat_type_id","Place_type_id") DO UPDATE SET {}'.format(','.join(fields), ','.join(markers), ','.join(update))
      dbClient.execute(con, sql, values)

    # Error
    except Exception as error:
      logger.error(error)
      con.rollback()
      log += 'Fila: ' + str(irow+3).zfill(4) + '. Contiene datos erróneos.\n'
      log += str(error) + '\n'
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
    log += 'Cargados ' + str(n_ok) + ' registro(s) correctamente\n'

   
  # Return
  return (n_ko == 0), log  