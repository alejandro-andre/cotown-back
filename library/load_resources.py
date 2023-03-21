# ###################################################
# Imports
# ###################################################


# ###################################################
# Load resources
# ###################################################

def load_resources(dbClient, data):

    # Return values
    n_ok = n_ko = 0
    log = ''

    # Header
    header = list(map(lambda cell: cell.value, data[2]))

    # Loop thru all rows skipping two first rows
    for irow, row in enumerate(data.iter_rows(min_row=3)):

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

            # Provider.Name
            elif column == 'Provider.Name':
                id = None
                if cell.value is not None and cell.value != '':
                    dbClient.select('SELECT id, "Name" FROM "Provider"."Provider" WHERE "Name"=%s', [cell.value])
                    aux = dbClient.fetch()
                    if aux is None:
                        log += 'Fila: ' + str(irow+2).zfill(4) + '. Proveedor "' + str(cell.value) + '" no encontrado\n'
                        ok = False
                    else:    
                        id = aux['id']
                record['Owner_id'] = id

            # Resource_flat_type.Code
            elif column == 'Flat_type.Code':
                id = None
                if cell.value is not None and cell.value != '':
                    dbClient.select('SELECT id, "Name" FROM "Resource"."Resource_flat_type" WHERE "Code"=%s', [cell.value])
                    aux = dbClient.fetch()
                    if aux is None:
                        log += 'Fila: ' + str(irow+2).zfill(4) + '. Tipo de piso "' + str(cell.value) + '" no encontrado\n'
                        ok = False
                    else:    
                        id = aux['id']
                record['Flat_type_id'] = id

            # Resource_place_type.Code
            elif column == 'Place_type.Code':
                id = None
                if cell.value is not None and cell.value != '':
                    dbClient.select('SELECT id, "Name" FROM "Resource"."Resource_place_type" WHERE "Code"=%s', [cell.value])
                    aux = dbClient.fetch()
                    if aux is None:
                        log += 'Fila: ' + str(irow+2).zfill(4) + '. Tipo de habitación/plaza "' + str(cell.value) + '" no encontrado\n'
                        ok = False
                    else:    
                        id = aux['id']
                record['Place_type_id'] = id

            # Pricing_rate.Code
            elif column == 'Pricing_rate.Code':
                id = None
                if cell.value is not None and cell.value != '':
                    dbClient.select('SELECT id, "Name" FROM "Billing"."Pricing_rate" WHERE "Code"=%s', [cell.value])
                    aux = dbClient.fetch()
                    if aux is None:
                        log += 'Fila: ' + str(irow+2).zfill(4) + '. Tarifa "' + str(cell.value) + '" no encontrada\n'
                        ok = False
                    else:    
                        id = aux['id']
                record['Rate_id'] = id

            # Copy cells
            else:
                record[column] = cell.value

        # Resource type
        if len(record['Code']) == 12:
            record['Resource_type'] = 'piso'
        elif len(record['Code']) == 16:
            record['Resource_type'] = 'habitacion'
        else:
            record['Resource_type'] = 'plaza'

        # Resource address
        record['Address'] = record['Address'] + ' ' + record['Code'][12:].replace('.', ' ')

        # Insert records
        fields = list(map(lambda key: '"' + key + '"', record.keys()))
        update = list(map(lambda key: '"'+ key + '"=EXCLUDED."' + key + '"', record.keys()))
        values = [record[field] for field in record.keys()]
        markers = ['%s'] * len(record.keys())
        sql = 'INSERT INTO "Resource"."Resource" ({}) VALUES ({}) ON CONFLICT ("Code") DO UPDATE SET {}'.format(','.join(fields), ','.join(markers), ','.join(update))
        try:
            dbClient.execute(sql, values)
        except:
            dbClient.rollback()
            log += 'Fila: ' + str(irow+2).zfill(4) + '. Contiene datos erróneos.\n'
            ok = False

        # Count oks and errors
        if ok:
            n_ok += 1
        else:
            n_ko += 1

    # Rollback?
    if n_ko > 0:
        dbClient.rollback()
        log += 'Analizados ' + str(n_ok) + ' registro(s) correctamente\n'
        log += 'Analizados ' + str(n_ko) + ' registro(s) con errores\n'
        log += 'No se han cargado datos\n'
    else:
        log += 'Cargados ' + str(n_ok) + ' registro(s) correctamente\n'

        
    # Return
    return (n_ko == 0), log  