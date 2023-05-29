# System includes
import json

# Cotown includes
from library.services.apiclient import APIClient
from library.services.utils import flatten_json
from library.business.print_contract import BOOKING, generate_doc_file

def main(tpl, id):

    # graphQL API
    apiClient = APIClient('experis.flows.ninja')
    apiClient.auth(user='modelsadmin', password='Ciber$2022')

    # Get booking
    booking = apiClient.call(BOOKING, { "id": id })
    if booking is None:
      return

    # Prepare booking
    context = flatten_json(booking['data'][0])
    print(json.dumps(context, indent=2))

    # Open template file
    fi = open(tpl + '.md', 'rb')
    template = fi.read()
    fi.close()

    # Generate rent contract
    file = generate_doc_file(context, template)
    with open(tpl + '.pdf', 'wb') as pdf:
        pdf.write(file.read())

if __name__ == '__main__':

    main('test/b2c-habitacion', 751)