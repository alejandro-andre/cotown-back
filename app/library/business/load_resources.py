# ###################################################
# Imports
# ###################################################

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Load resources
# ###################################################

def load_resources(dbClient, con, data):

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
      extras = []
      unavail = {}

      # Ok by default
      ok = True

      # Loop thru each column
      for icol, cell in enumerate(row):

        # Column
        column = header[icol]

        # Discard some columns
        if column is None or isinstance(column, int):
          pass

        # Provider.Name
        elif column == 'Owner.Name':
          id = None
          if cell.value is not None and cell.value != '':
            cur = dbClient.execute(con, 'SELECT id, "Name" FROM "Provider"."Provider" WHERE "Name"=%s', [cell.value])
            aux = cur.fetchone()
            cur.close()
            if aux is None:
              log += 'Fila: ' + str(irow+3).zfill(4) + '. Proveedor "' + str(cell.value) + '" no encontrado\n'
              ok = False
            else: 
              id = aux['id']
          record['Owner_id'] = id

        # Service.Name
        elif column == 'Service.Name':
          id = None
          if cell.value is not None and cell.value != '':
            cur = dbClient.execute(con, 'SELECT id, "Name" FROM "Provider"."Provider" WHERE "Name"=%s', [cell.value])
            aux = cur.fetchone()
            cur.close()
            if aux is None:
              log += 'Fila: ' + str(irow+3).zfill(4) + '. Proveedor "' + str(cell.value) + '" no encontrado\n'
              ok = False
            else: 
              id = aux['id']
          record['Service_id'] = id

        # Resource_flat_type.Code
        elif column == 'Flat_type.Code':
          id = None
          if cell.value is not None and cell.value != '':
            cur = dbClient.execute(con, 'SELECT id, "Name" FROM "Resource"."Resource_flat_type" WHERE "Code"=%s', [cell.value])
            aux = cur.fetchone()
            cur.close()
            if aux is None:
              log += 'Fila: ' + str(irow+3).zfill(4) + '. Tipo de piso "' + str(cell.value) + '" no encontrado\n'
              ok = False
            else: 
              id = aux['id']
          record['Flat_type_id'] = id

        # Resource_flat_subtype.Code
        elif column == 'Flat_subtype.Code':
          id = None
          if cell.value is not None and cell.value != '':
            cur = dbClient.execute(con, 'SELECT id, "Name" FROM "Resource"."Resource_flat_subtype" WHERE "Code"=%s', [cell.value])
            aux = cur.fetchone()
            cur.close()
            if aux is None:
              log += 'Fila: ' + str(irow+3).zfill(4) + '. Subtipo de piso "' + str(cell.value) + '" no encontrado\n'
              ok = False
            else: 
              id = aux['id']
          record['Flat_subtype_id'] = id

        # Resource_place_type.Code
        elif column == 'Place_type.Code':
          id = None
          if cell.value is not None and cell.value != '':
            cur = dbClient.execute(con, 'SELECT id, "Name" FROM "Resource"."Resource_place_type" WHERE "Code"=%s', [cell.value])
            aux = cur.fetchone()
            cur.close()
            if aux is None:
              log += 'Fila: ' + str(irow+3).zfill(4) + '. Tipo de habitación/plaza "' + str(cell.value) + '" no encontrado\n'
              ok = False
            else: 
              id = aux['id']
          record['Place_type_id'] = id

        # Pricing_rate.Code
        elif column == 'Pricing_rate.Code':
          id = None
          if cell.value is not None and cell.value != '':
            cur = dbClient.execute(con, 'SELECT id, "Name" FROM "Billing"."Pricing_rate" WHERE "Code"=%s', [cell.value])
            aux = cur.fetchone()
            cur.close()
            if aux is None:
              log += 'Fila: ' + str(irow+3).zfill(4) + '. Tarifa "' + str(cell.value) + '" no encontrada\n'
              ok = False
            else: 
              id = aux['id']
          record['Rate_id'] = id

        # Extras
        elif column == '[extras]':
          if cell.value is not None:
            extras = [e.strip() for e in cell.value.split(',')]

        # Special cells
        elif column[0] == '[':
          if cell.value is not None:
            unavail[column[1:-1]] = cell.value

        # Copy cells
        else:
          record[column] = cell.value

      # Building
      cur = dbClient.execute(con, 'SELECT id FROM "Building"."Building" WHERE "Code"=%s', (record['Code'][:6],))
      aux = cur.fetchone()
      cur.close()
      if aux is None:
        log += 'Fila: ' + str(irow+3).zfill(4) + '. Edificio "' + record['Code'][:6] + '" no encontrado\n'
        ok = False
      else: 
        record['Building_id'] = aux['id']

      # Flat
      record['Flat_id'] = None
      record['Room_id'] = None
      if len(record['Code']) == 12:
        record['Resource_type'] = 'piso'

      # Room
      elif len(record['Code']) == 16:
        record['Resource_type'] = 'habitacion'
        cur = dbClient.execute(con, 'SELECT id FROM "Resource"."Resource" WHERE "Code"=%s', (record['Code'][:12],))
        aux = cur.fetchone()
        cur.close()
        if aux is None:
          log += 'Fila: ' + str(irow+3).zfill(4) + '. Piso "' + record['Code'][:12] + '" no encontrado\n'
          ok = False
        else: 
          record['Flat_id'] = aux['id']

      # Place
      else:
        record['Resource_type'] = 'plaza'
        cur = dbClient.execute(con, 'SELECT id FROM "Resource"."Resource" WHERE "Code"=%s', (record['Code'][:12],))
        aux = cur.fetchone()
        cur.close()
        if aux is None:
          log += 'Fila: ' + str(irow+3).zfill(4) + '. Piso "' + record['Code'][:12] + '" no encontrado\n'
          ok = False
        else: 
          record['Flat_id'] = aux['id']
        cur = dbClient.execute(con, 'SELECT id FROM "Resource"."Resource" WHERE "Code"=%s', (record['Code'][:16],))
        aux = cur.fetchone()
        cur.close()
        if aux is None:
          log += 'Fila: ' + str(irow+3).zfill(4) + '. Habitación "' + record['Code'][:12] + '" no encontrada\n'
          ok = False
        else: 
          record['Room_id'] = aux['id']

      # Resource address
      record['Street']  = record['Street']
      record['Address'] = record['Address']
    
      # Insert record
      fields = list(map(lambda key: '"' + key + '"', record.keys()))
      update = list(map(lambda key: '"'+ key + '"=EXCLUDED."' + key + '"', record.keys()))
      values = [record[field] for field in record.keys()]
      markers = ['%s'] * len(record.keys())
      sql = 'INSERT INTO "Resource"."Resource" ({}) VALUES ({}) ON CONFLICT ("Code") DO UPDATE SET {} RETURNING ID'.format(','.join(fields), ','.join(markers), ','.join(update))
      cur = dbClient.execute(con, sql, values)
      id = cur.fetchone()[0]

      # Extras
      dbClient.execute(con, 'DELETE FROM "Resource"."Resource_amenity" WHERE "Resource_id" = %s', (id,))
      for item in extras:
        cur = dbClient.execute(con, 'SELECT id FROM "Resource"."Resource_amenity_type" WHERE "Code" = %s', (item,))
        aux = cur.fetchone()
        cur.close()
        if aux is None:
          log += 'Fila: ' + str(irow+3).zfill(4) + '. Extra "' + item + '" no encontrado\n'
          ok = False
        else: 
          dbClient.execute(con, 
          '''
          INSERT INTO "Resource"."Resource_amenity"
          ("Resource_id", "Amenity_type_id")
          VALUES (%s, %s)
          ''', 
          (id, aux[0]))

      # Unavailability
      dbClient.execute(con, 'DELETE FROM "Resource"."Resource_availability" WHERE "Resource_id" = %s', (id,))
      if unavail != {}:
        cur = dbClient.execute(con, 'SELECT id FROM "Resource"."Resource_status" WHERE "Name" = %s', (unavail['unavailable'],))
        aux = cur.fetchone()
        cur.close()
        if aux is None:
          log += 'Fila: ' + str(irow+3).zfill(4) + '. Código de no disponibilidad "' + unavail['unavailable'] + '" no encontrado\n'
          ok = False
        else: 
          dbClient.execute(con, 
          '''
          INSERT INTO "Resource"."Resource_availability"
          ("Resource_id", "Status_id", "Date_from", "Date_to")
          VALUES (%s, %s, %s, %s)
          ''', 
          (id, aux[0], unavail['from'], unavail['to']))

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

  # Update availabilities
  if n_ko == 0:
    dbClient.execute(con, 'UPDATE "Resource"."Resource_availability" SET id=id')

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