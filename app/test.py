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
from library.business.contract import BOOKING, GROUP_BOOKING, generate_doc_file

logger = logging.getLogger('COTOWN')

CONTRACTS_DIR = 'contracts'


def load_local_template(filename):
    path = os.path.join(CONTRACTS_DIR, filename)
    if not os.path.isfile(path):
        logger.error('Plantilla no encontrada: %s', path)
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def generate_b2c(apiClient, id, template_file):

    # Obtener datos completos de la reserva individual
    result = apiClient.call(BOOKING, { 'id': id })
    if not result or not result['data']:
        logger.error('Reserva %s no encontrada', id)
        return

    # Aplanar la estructura anidada GraphQL a un dict plano
    context = flatten(result['data'][0])

    # Test
    context['Booking_type'] = 'limitado'
    context['Booking_limit_type'] = 'lau'

    # Cargar plantilla local y generar PDF
    template = load_local_template(template_file)
    if template is None:
        return
    pdf = generate_doc_file(context, template)
    out = f'contract_b2c.pdf'
    with open(out, 'wb') as f:
        f.write(pdf.read())
    logger.info('PDF guardado: %s', out)


def generate_b2b(apiClient, id, template_file):

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

    # Test
    context['Booking_type'] = 'limitado'
    context['Booking_limit_type'] = 'lau'

    # Construir lista de pisos asignados (por dirección si existe, sino por código)
    try:
        context['Flats'] = ', '.join(sorted(list({r['Resource_flat_address'] for r in context['Rooms']})))
    except:
        context['Flats'] = ', '.join(sorted(list({r['Resource_code'] for r in context['Rooms']})))

    # Cargar plantilla local y generar PDF
    template = load_local_template(template_file)
    if template is None:
        return
    pdf = generate_doc_file(context, template)
    out = f'contract_b2b.pdf'
    with open(out, 'wb') as f:
        f.write(pdf.read())
    logger.info('PDF guardado: %s', out)


def main():

    # Definir argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Genera el PDF de contrato para una reserva sin enviarlo.')
    parser.add_argument('--id',       type=int, required=True, help='Número de reserva')
    parser.add_argument('--type',     choices=['B2C', 'B2B'], default='B2C', help='Tipo de reserva (B2C individual / B2B grupo)')
    parser.add_argument('--template', required=True, help='Nombre del fichero de plantilla en contracts/')
    args = parser.parse_args()

    # Autenticar contra la API GraphQL
    apiClient = APIClient(settings.SERVER)
    apiClient.auth(user=settings.GQLUSER, password=settings.GQLPASS)

    # Delegar en la función correspondiente según el tipo de reserva
    if args.type == 'B2C':
        generate_b2c(apiClient, args.id, args.template)
    else:
        generate_b2b(apiClient, args.id, args.template)


if __name__ == '__main__':
    main()
