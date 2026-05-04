# ###################################################
# Test script
# ---------------------------------------------------
# Generates a contract PDF for a given booking ID
# using a local template file. Does NOT upload,
# save to DB, or send to DocuSign.
#
# Usage:
#   python test_printcontract.py --id 1234 --template my_template.md
#   python test_printcontract.py --id 1234 --template my_template.md --type B2B
# ###################################################

import argparse
import logging
import os

from library.services.config import settings
from library.services.apiclient import APIClient
from library.services.utils import flatten
from library.business.contract import BOOKING, GROUP_BOOKING, generate_doc_file, merge_pdfs, fetch_annexes

logger = logging.getLogger('COTOWN')


def load_local_template(filename):
    path = os.path.join('contracts', filename)
    if not os.path.isfile(path):
        logger.error('Plantilla no encontrada: %s', path)
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def generate_b2c(apiClient, id, template_file, contract='rent'):

    # Obtener datos completos de la reserva individual
    result = apiClient.call(BOOKING, { 'id': id })
    if not result or not result['data']:
        logger.error('Reserva %s no encontrada', id)
        return

    # Aplanar la estructura anidada GraphQL a un dict plano
    context = flatten(result['data'][0])

    # Cargar plantilla local y generar PDF
    template = load_local_template(template_file)
    if template is None:
        return
    pdf = generate_doc_file(context, template)

    # Obtener documentos anexos y fusionar (solo renta + Barcelona, ordenados alfabéticamente)
    annex_pairs = []
    if contract == 'rent' and context.get('Resource_location_id') == 1:
        rid = context.get('Resource_flat_id') or context.get('Resource_id')
        building_docs, resource_docs = fetch_annexes(apiClient, [rid])
        for doc in building_docs:
            resp = apiClient.getFile(doc['id'], 'Building/Building_doc', 'Document')
            if resp and resp.content:
                annex_pairs.append((doc.get('Name', ''), resp.content))
                logger.info('Anexo edificio añadido: %s', doc.get('Name', doc['id']))
        for doc in resource_docs:
            resp = apiClient.getFile(doc['id'], 'Resource/Resource_doc', 'Document')
            if resp and resp.content:
                annex_pairs.append((doc.get('Name', ''), resp.content))
                logger.info('Anexo recurso añadido: %s', doc.get('Name', doc['id']))
    annex_pairs.sort(key=lambda x: x[0])
    annex_data = [content for _, content in annex_pairs]

    # Guardar contrato (con anexos si los hay)
    merged = merge_pdfs(pdf, annex_data) if annex_data else pdf
    out = f'contracts/test/contract_b2c_{id}_{contract}.pdf'
    with open(out, 'wb') as f:
        f.write(merged.read())
    logger.info('PDF guardado: %s (%d anexos)', out, len(annex_data))


def generate_b2b(apiClient, id, template_file, contract='rent'):

    # Obtener datos completos de la reserva de grupo
    result = apiClient.call(GROUP_BOOKING, { 'id': id })
    if not result or not result['data']:
        logger.error('Reserva grupo %s no encontrada', id)
        return

    # Aplanar la estructura anidada GraphQL a un dict plano
    context = flatten(result['data'][0])
    if not context['Rooms']:
        logger.error('La reserva grupo %s no tiene habitaciones', id)
        return

    # Consolidate flats
    flats_dict = {}
    for room in context['Rooms']:
      if room.get('Resource_flat_code'):
        flats_dict[room['Resource_flat_code']] = {
          k: v for k, v in room.items() if k.startswith('Resource_flat_')
        }
    context['Flats_info'] = list(flats_dict.values())
    context['Flats'] = ', '.join(sorted(f['Resource_flat_address'] for f in context['Flats_info']))
    print(context['Flats'])

    # Cargar plantilla local y generar PDF
    template = load_local_template(template_file)
    if template is None:
        return
    pdf = generate_doc_file(context, template)

    # Obtener documentos anexos y fusionar (solo renta + Barcelona, ordenados alfabéticamente)
    annex_pairs = []
    if contract == 'rent' and context.get('Rooms')[0].get('Resource_location_id') == 1:
        rid = [r.get('Resource_id') for r in context.get('Rooms')]
        building_docs, resource_docs = fetch_annexes(apiClient, rid)
        for doc in building_docs:
            resp = apiClient.getFile(doc['id'], 'Building/Building_doc', 'Document')
            if resp and resp.content:
                annex_pairs.append((doc.get('Name', ''), resp.content))
                logger.info('Anexo edificio añadido: %s', doc.get('Name', doc['id']))
        for doc in resource_docs:
            resp = apiClient.getFile(doc['id'], 'Resource/Resource_doc', 'Document')
            if resp and resp.content:
                annex_pairs.append((doc.get('Name', ''), resp.content))
                logger.info('Anexo recurso añadido: %s', doc.get('Name', doc['id']))
    annex_pairs.sort(key=lambda x: x[0])
    annex_data = [content for _, content in annex_pairs]

    # Guardar contrato (con anexos si los hay)
    merged = merge_pdfs(pdf, annex_data) if annex_data else pdf
    out = f'contracts/test/contract_b2c_{id}_{contract}.pdf'
    with open(out, 'wb') as f:
        f.write(merged.read())
    logger.info('PDF guardado: %s (%d anexos)', out, len(annex_data))

def main():

    # Definir argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Genera el PDF de contrato para una reserva sin enviarlo.')
    parser.add_argument('--id',       type=int, required=True, help='Número de reserva')
    parser.add_argument('--type',     choices=['B2C', 'B2B'], default='B2C', help='Tipo de reserva (B2C individual / B2B grupo)')
    parser.add_argument('--contract', choices=['rent', 'services'], default='rent', help='Tipo de contrato (rent / services)')
    parser.add_argument('--template', required=True, help='Nombre del fichero de plantilla en contracts/')
    args = parser.parse_args()

    # Autenticar contra la API GraphQL
    apiClient = APIClient(settings.SERVER)
    apiClient.auth(user=settings.GQLUSER, password=settings.GQLPASS)

    # Delegar en la función correspondiente según el tipo de reserva
    if args.type == 'B2C':
        generate_b2c(apiClient, args.id, args.template, args.contract)
    else:
        generate_b2b(apiClient, args.id, args.template, args.contract)


if __name__ == '__main__':
    main()
