# ###################################################
# Imports
# ###################################################

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Load inventory
# ###################################################

def load_inventory(dbClient, con, data):

  # Delete
  sql = 'DELETE FROM "Resource"."Resource_inventory"'
  dbClient.execute(con, sql, values)

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

        # Resource.Code
        elif column == 'Resource.Code':
          cur = dbClient.execute(con, 'SELECT id FROM "Resource"."Resource" WHERE "Code"=%s', (cell.value,))
          aux = cur.fetchone()
          cur.close()
          if aux is None:
            log += 'Fila: ' + str(irow+3).zfill(4) + '. Recurso "' + str(cell.value) + '" no encontrado\n'
            ok = False
          else: 
            record['Resource_id'] = aux['id']

        # Inventory_type.Name
        elif column == 'Inventory_type.Name':
          id = None
          if cell.value is not None and cell.value != '':
            cur = dbClient.execute(con, 'SELECT id FROM "Resource"."Resource_inventory_type" WHERE "Name"=%s', (cell.value,))
            aux = cur.fetchone()
            cur.close()
            if aux is None:
              log += 'Fila: ' + str(irow+3).zfill(4) + '. Tipo de inventario "' + str(cell.value) + '" no encontrado\n'
              ok = False
            else: 
              id = aux['id']
          record['Inventory_type_id'] = id

        # Inventory_zone.Name
        elif column == 'Inventory_zone.Name':
          id = None
          if cell.value is not None and cell.value != '':
            cur = dbClient.execute(con, 'SELECT id FROM "Resource"."Resource_inventory_zone" WHERE "Name"=%s', (cell.value,))
            aux = cur.fetchone()
            cur.close()
            if aux is None:
              log += 'Fila: ' + str(irow+3).zfill(4) + '. Zona de inventario "' + str(cell.value) + '" no encontrada\n'
              ok = False
            else: 
              id = aux['id']
          record['Inventory_zone_id'] = id

        # Copy cells
        else:
          record[column] = cell.value

      # Insert records
      fields = list(map(lambda key: '"' + key + '"', record.keys()))
      values = [record[field] for field in record.keys()]
      markers = ['%s'] * len(record.keys())
      sql = 'INSERT INTO "Resource"."Resource_inventory" ({}) VALUES ({})'.format(','.join(fields), ','.join(markers))
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