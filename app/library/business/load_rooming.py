# ###################################################
# Imports
# ###################################################

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Load resources
# ###################################################

def load_rooming(dbClient, con, data):

  # Return values
  n_ok = n_ko = 0
  log = ''

  # Get booking 
  booking_id = data['A5'].value

  # Check booking status
  cur = dbClient.execute(con, 'SELECT "Status" FROM "Booking"."Booking_group" WHERE id=%s', [booking_id])
  aux = cur.fetchone()
  if aux is None:
    log += 'Reserva desconocida\n'
    return False, log  
  #if aux['Status'] not in ('grupobloqueado', 'grupoconfirmado', 'inhouse'):
  #  log += 'Reserva no activa. No se han cargado datos\n'
  #  return False, log  

  # Header
  header = list(map(lambda cell: cell.value, data[4]))

  # Loop thru all rows skipping four first rows
  for irow, row in enumerate(data.iter_rows(min_row=5)):
    # Skip empty rows
    if row[1].value is None or row[1].value == '':
      continue

    # Process
    try:

      # Empty record
      record = {}

      # Ok
      ok = True

      # Loop thru each column
      for icol, cell in enumerate(row):

        # Column
        column = header[icol]

        # Discard some columns
        if column is None or isinstance(column, int):
          pass

        # Resource.Name
        elif column == 'Resource.Code':
          id = None
          if cell.value is not None and cell.value != '':
            cur = dbClient.execute(
              con, 
              'SELECT id, "Code" FROM "Booking"."Booking_group_rooms" WHERE "Booking_id"=%s AND "Code"=%s', [booking_id, cell.value]
            )
            aux = cur.fetchone()
            cur.close()
            if aux is None:
              log += 'Fila: ' + str(irow+3).zfill(4) + '. Recurso "' + str(cell.value) + '" no encontrado\n'
              ok = False
            else: 
              id = aux['id']
          record['Room_id'] = id

        # Id_type.Name
        elif column == 'Id_type.Name':
          id = None
          if cell.value is not None and cell.value != '':
            cur = dbClient.execute(con, 'SELECT id, "Name" FROM "Auxiliar"."Id_type" WHERE "Name"=%s', [cell.value])
            aux = cur.fetchone()
            cur.close()
            if aux is None:
              log += 'Fila: ' + str(irow+3).zfill(4) + '. Tipo de Id "' + str(cell.value) + '" no encontrado\n'
              ok = False
            else: 
              id = aux['id']
          record['Id_type_id'] = id

        # Gender.Name
        elif column == 'Gender.Name':
          id = None
          if cell.value is not None and cell.value != '':
            cur = dbClient.execute(con, 'SELECT id, "Name" FROM "Auxiliar"."Gender" WHERE "Name"=%s', [cell.value])
            aux = cur.fetchone()
            cur.close()
            if aux is None:
              log += 'Fila: ' + str(irow+3).zfill(4) + '. Género "' + str(cell.value) + '" no encontrado\n'
              ok = False
            else: 
              id = aux['id']
          record['Gender_id'] = id

        # Language.Name
        elif column == 'Language.Name':
          id = None
          if cell.value is not None and cell.value != '':
            cur = dbClient.execute(con, 'SELECT id, "Name" FROM "Auxiliar"."Language" WHERE "Name"=%s', [cell.value])
            aux = cur.fetchone()
            cur.close()
            if aux is None:
              log += 'Fila: ' + str(irow+3).zfill(4) + '. Idioma "' + str(cell.value) + '" no encontrado\n'
              ok = False
            else: 
              id = aux['id']
          record['Language_id'] = id

        # Country.Name
        elif column == 'Country.Name':
          id = None
          if cell.value is not None and cell.value != '':
            cur = dbClient.execute(con, 'SELECT id, "Name" FROM "Geo"."Country" WHERE "Name"=%s', [cell.value])
            aux = cur.fetchone()
            cur.close()
            if aux is None:
              log += 'Fila: ' + str(irow+3).zfill(4) + '. País "' + str(cell.value) + '" no encontrado\n'
              ok = False
            else: 
              id = aux['id']
          record['Country_id'] = id

        # Nationality.Name
        elif column == 'Nationality.Name':
          id = None
          if cell.value is not None and cell.value != '':
            cur = dbClient.execute(con, 'SELECT id, "Name" FROM "Geo"."Country" WHERE "Name"=%s', [cell.value])
            aux = cur.fetchone()
            cur.close()
            if aux is None:
              log += 'Fila: ' + str(irow+3).zfill(4) + '. Nacionalidad "' + str(cell.value) + '" no encontrada\n'
              ok = False
            else: 
              id = aux['id']
          record['Nationality_id'] = id

        # Origin.Name
        elif column == 'Country_origin.Name':
          id = None
          if cell.value is not None and cell.value != '':
            cur = dbClient.execute(con, 'SELECT id, "Name" FROM "Geo"."Country" WHERE "Name"=%s', [cell.value])
            aux = cur.fetchone()
            cur.close()
            if aux is None:
              log += 'Fila: ' + str(irow+3).zfill(4) + '. País de origen "' + str(cell.value) + '" no encontrado\n'
              ok = False
            else: 
              id = aux['id']
          record['Country_origin_id'] = id

        # Copy cells
        else:
          record[column] = cell.value

      # Update record
      keys = [k for k in list(record.keys()) if k not in ('Booking_id', 'Group_code', 'Room_id')] 
      update_fields = [f'"{key}" = %s' for key in keys]
      update_values = [record[key] for key in keys + ['Booking_id', 'Group_code', 'Room_id']]
      update_sql = 'UPDATE "Booking"."Booking_group_rooming" SET {} WHERE "Booking_id"=%s AND "Group_code"=%s and "Room_id"=%s'.format(','.join(update_fields))

      # Or insert record
      insert_fields = list(map(lambda key: '"' + key + '"', record.keys()))
      insert_update = list(map(lambda key: '"'+ key + '"=EXCLUDED."' + key + '"', record.keys()))
      insert_values = [record[field] for field in record.keys()]
      markers = ['%s'] * len(record.keys())
      insert_sql = 'INSERT INTO "Booking"."Booking_group_rooming" ({}) VALUES ({}) ON CONFLICT ("Booking_id", "Group_code", "Room_id") DO UPDATE SET {} '.format(','.join(insert_fields), ','.join(markers), ','.join(insert_update))

      # Execute
      cur = dbClient.execute(con, update_sql, update_values)
      if cur.rowcount == 0:
        cur = dbClient.execute(con, insert_sql, insert_values)

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
    log += 'Cargados ' + str(n_ok) + ' registro(s) correctamente\n'

   
  # Return
  return (n_ko == 0), log  
