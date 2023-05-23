# System includes
from io import BytesIO

# Cotown includes
from library.services.apiclient import APIClient
from library.services.utils import flatten_json
from library.business.print_contract import BOOKING, generate_doc_file

def main(id):

    # graphQL API
    apiClient = APIClient('experis.flows.ninja')
    apiClient.auth(user='modelsadmin', password='Ciber$2022')

    # Get booking
    booking = apiClient.call(BOOKING, { "id": id })
    if booking is None:
      return

    # Prepare booking
    context = flatten_json(booking['data'][0])
    print(context)

    # Open template file
    fi = open('test.md', 'rb')
    template = fi.read()
    fi.close()

    # Generate rent contract
    file = generate_doc_file(context, template)
    with open('test.pdf', 'wb') as pdf:
        pdf.write(file.read())

if __name__ == '__main__':

    main(453)