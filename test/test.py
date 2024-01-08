# System includes
import json

# Cotown includes
from library.services.apiclient import APIClient
from library.services.utils import flatten
from library.business.print_contract import BOOKING, generate_doc_file

def main(q, tpl, id):

  # graphQL API
  apiClient = APIClient('core.cotown.com')
  apiClient.auth(user='modelsadmin', password='Ciber$2022')

  # Get booking
  booking = apiClient.call(q, { "id": id })
  if booking is None:
    return

  # Prepare booking
  context = flatten(booking['data'][0])

  # Open template file
  fi = open(tpl + '.md', 'r')
  template = fi.read()
  fi.close()

  # Generate rent contract
  file = generate_doc_file(context, template)
  with open(tpl + '.pdf', 'wb') as pdf:
    pdf.write(file.read())

if __name__ == '__main__':

  print('Testing...')
  main(BOOKING, 'test', 5602)
