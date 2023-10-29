# System includes
import json

# Cotown includes
from library.services.apiclient import APIClient
from library.services.utils import flatten
from library.business.print_contract import age, BOOKING, GROUP_BOOKING, generate_doc_file

def main(q, tpl, id):

   # graphQL API
   apiClient = APIClient('experis.flows.ninja')
   apiClient.auth(user='modelsadmin', password='Ciber$2022')

   # Get booking
   booking = apiClient.call(q, { "id": id })
   if booking is None:
     return

   # Prepare booking
   context = flatten(booking['data'][0])
   #print(json.dumps(context, indent=2))

   # Consolidate flats
   if context.get('Rooms'):
     context['Flats'] = ', '.join(list({r["Resource_flat_address"] for r in context['Rooms']}))

   # Open template file
   fi = open(tpl + '.md', 'rb')
   template = fi.read()
   fi.close()

   # Generate rent contract
   file = generate_doc_file(context, template)
   with open(tpl + '.pdf', 'wb') as pdf:
       pdf.write(file.read())

if __name__ == '__main__':

   print('Testing...')
   #main(GROUP_BOOKING, 'upload/contracts/Provider.Provider_template.Template/b2b_vandor', 1)
   main(BOOKING, 'upload/contracts/Provider.Provider_template.Template/b2c_vandor', 1)
   #main(BOOKING, 'upload/contracts/Provider.Provider_template.Template/b2c_servicios', 3)
   #main(BOOKING, 'upload/contracts/Provider.Provider_template.Template/b2c_piso_completo', 6)
   #main(BOOKING, 'upload/contracts/Provider.Provider_template.Template/residencia', 5)
