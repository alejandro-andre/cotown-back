# ###################################################
# Imports
# ###################################################

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Preload lookup table
# ###################################################

def preload_lookup(dbClient, con, sql, key_col):

  # Execute and build dict
  cur = dbClient.execute(con, sql)
  result = {row[key_col]: row['id'] for row in cur.fetchall()}
  cur.close()

  # Return
  return result


# ###################################################
# Resolve lookup value
# ###################################################

def resolve_lookup(cache, value, label, irow, log):

  # Empty value
  if not value and value != 0:
    return None, True

  # Lookup
  resolved = cache.get(value)

  # Not found
  if resolved is None:
    log.append('Fila: ' + str(irow).zfill(4) + '. ' + label + ' "' + str(value) + '" no encontrado')
    return None, False

  # Return
  return resolved, True


# ###################################################
# Load resources
# ###################################################

def load_resources(dbClient, con, data):

  # Return values
  n_ok = n_ko = 0
  log = []

  # Pre-load all lookup tables
  providers     = preload_lookup(dbClient, con, 'SELECT id, "Name" FROM "Provider"."Provider"', 'Name')
  flat_types    = preload_lookup(dbClient, con, 'SELECT id, "Code" FROM "Resource"."Resource_flat_type"', 'Code')
  flat_subs     = preload_lookup(dbClient, con, 'SELECT id, "Code" FROM "Resource"."Resource_flat_subtype"', 'Code')
  place_types   = preload_lookup(dbClient, con, 'SELECT id, "Code" FROM "Resource"."Resource_place_type"', 'Code')
  rates         = preload_lookup(dbClient, con, 'SELECT id, "Code" FROM "Billing"."Pricing_rate"', 'Code')
  usages        = preload_lookup(dbClient, con, 'SELECT id, "Name" FROM "Resource"."Resource_usage"', 'Name')
  buildings     = preload_lookup(dbClient, con, 'SELECT id, "Code" FROM "Building"."Building"', 'Code')
  resources     = preload_lookup(dbClient, con, 'SELECT id, "Code" FROM "Resource"."Resource"', 'Code')
  amenity_types = preload_lookup(dbClient, con, 'SELECT id, "Code" FROM "Resource"."Resource_amenity_type"', 'Code')

  # Header
  header = [cell.value for cell in data[2]]

  # Loop thru all rows skipping two first rows
  for irow, row in enumerate(data.iter_rows(min_row=3)):
    row_num = irow + 3

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

        # Provider.Name
        elif column == 'Owner.Name':
          record['Owner_id'], ok_i = resolve_lookup(providers, cell.value, 'Proveedor', row_num, log)
          ok = ok and ok_i

        # Service.Name
        elif column == 'Service.Name':
          record['Service_id'], ok_i = resolve_lookup(providers, cell.value, 'Proveedor', row_num, log)
          ok = ok and ok_i

        # Resource_flat_type.Code
        elif column == 'Flat_type.Code':
          record['Flat_type_id'], ok_i = resolve_lookup(flat_types, cell.value, 'Tipo de piso', row_num, log)
          ok = ok and ok_i

        # Resource_flat_subtype.Code
        elif column == 'Flat_subtype.Code':
          record['Flat_subtype_id'], ok_i = resolve_lookup(flat_subs, cell.value, 'Subtipo de piso', row_num, log)
          ok = ok and ok_i

        # Resource_place_type.Code
        elif column == 'Place_type.Code':
          record['Place_type_id'], ok_i = resolve_lookup(place_types, cell.value, 'Tipo de habitación/plaza', row_num, log)
          ok = ok and ok_i

        # Pricing_rate.Code
        elif column == 'Pricing_rate.Code':
          record['Rate_id'], ok_i = resolve_lookup(rates, cell.value, 'Tarifa', row_num, log)
          ok = ok and ok_i

        # Resource_usage.Name
        elif column == 'Resource_usage.Name':
          record['Usage_id'], ok_i = resolve_lookup(usages, cell.value, 'Uso', row_num, log)
          ok = ok and ok_i

        # Extras
        elif column == '[extras]':
          if cell.value is not None:
            extras = [e.strip() for e in cell.value.split(',')]

        # Copy cells
        else:
          record[column] = cell.value

      # Building
      building_id = buildings.get(record.get('Code', '')[:6])
      if building_id is None:
        log.append('Fila: ' + str(row_num).zfill(4) + '. Edificio "' + record['Code'][:6] + '" no encontrado')
        ok = False
      else:
        record['Building_id'] = building_id

      # Flat
      record['Flat_id'] = None
      record['Room_id'] = None

      # Room
      if record['Resource_type'] == 'habitacion':
        flat_id = resources.get(record['Code'][:12])
        if flat_id is None:
          log.append('Fila: ' + str(row_num).zfill(4) + '. Piso "' + record['Code'][:12] + '" no encontrado')
          ok = False
        else:
          record['Flat_id'] = flat_id

      # Place
      if record['Resource_type'] == 'plaza':
        flat_id = resources.get(record['Code'][:12])
        if flat_id is None:
          log.append('Fila: ' + str(row_num).zfill(4) + '. Piso "' + record['Code'][:12] + '" no encontrado')
          ok = False
        else:
          record['Flat_id'] = flat_id
        room_id = resources.get(record['Code'][:16])
        if room_id is None:
          log.append('Fila: ' + str(row_num).zfill(4) + '. Habitación "' + record['Code'][:16] + '" no encontrada')
          ok = False
        else:
          record['Room_id'] = room_id

      # Insert record
      keys    = list(record.keys())
      fields  = list(map(lambda k: '"' + k + '"', keys))
      update  = list(map(lambda k: '"' + k + '"=EXCLUDED."' + k + '"', keys))
      values  = [None if record[k] == '' else record[k] for k in keys]
      markers = ['%s'] * len(keys)
      sql = 'INSERT INTO "Resource"."Resource" ({}) VALUES ({}) ON CONFLICT ("Code") DO UPDATE SET {} RETURNING id'.format(','.join(fields), ','.join(markers), ','.join(update))
      cur = dbClient.execute(con, sql, values)
      id = cur.fetchone()[0]
      cur.close()

      # Extras
      dbClient.execute(con, 'DELETE FROM "Resource"."Resource_amenity" WHERE "Resource_id" = %s', (id,))
      for u_res in extras:
        amenity_id = amenity_types.get(u_res)
        if amenity_id is None:
          log.append('Fila: ' + str(row_num).zfill(4) + '. Extra "' + u_res + '" no encontrado')
          ok = False
        else:
          dbClient.execute(con,
          '''
          INSERT INTO "Resource"."Resource_amenity"
          ("Resource_id", "Amenity_type_id")
          VALUES (%s, %s)
          ''',
          (id, amenity_id))

      # Log
      logger.info(record['Code'])

    # Error
    except Exception as error:
      logger.error(error)
      con.rollback()
      log.append('Fila: ' + str(row_num).zfill(4) + '. Contiene datos erróneos.')
      e = str(error)
      if (e.startswith('!!!')):
        log.append(e.split('!!!')[2])
      else:
        log.append(e)
      ok = False

    # Count oks and errors
    if ok:
      n_ok += 1
    else:
      n_ko += 1

  # Rollback?
  if n_ko > 0:
    con.rollback()
    log.append('Analizados ' + str(n_ok) + ' registro(s) correctamente')
    log.append('Analizados ' + str(n_ko) + ' registro(s) con errores')
    log.append('No se han cargado datos')
  else:
    con.commit()
    log.append('Cargados ' + str(n_ok) + ' registro(s) correctamente')

  # Return
  return (n_ko == 0), '\n'.join(log)