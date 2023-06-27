# ##################################################
# Imports
# ##################################################

import os
os.add_dll_directory('C:\Program Files\GTK3-Runtime Win64\lib')

from PIL import Image
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from io import BytesIO
import cairosvg
import base64
import mimetypes
import requests
import sys


# ##################################################
# Constants
# ##################################################

SERVER = 'experis.flows.ninja'
#SERVER = 'core.cotown.com'
USER   = 'modelsadmin'
PASS   = 'Ciber$2022'


# ##################################################
# Upload files to Airflows
# ##################################################

def upload(folder, wildcard):

  # Get token
  client = Client(transport=AIOHTTPTransport(url='https://' + SERVER + '/graphql'), fetch_schema_from_transport=True)
  result = client.execute(gql('mutation { login(username:"' + USER + '", password:"' + PASS + '") }'))
  token = result['login']

  # Upload all files
  for root, dirs, files in os.walk(folder):

    # Folders
    for dir in dirs:

      # Discard not matching folders
      if wildcard != '*' and wildcard not in dir:
        continue

      # Schema, entity and field
      print(dir)
      schema, entity, field = dir.split('.')

      # graphQL query
      query = '{data:' + schema + '_' + entity + 'List{id ' + field + '{name width}}}'
      vars = { 'authorization': token }
      result = client.execute(gql(query), vars)

      # Process each record
      for item in result['data']:
        if item[field]:

          # Skip already loaded
          #if item[field]['width'] and item[field]['width'] > 10:
          #  continue

          try:
            # File info
            id = item['id'] 
            name = item[field]['name'] 
            path = root + '/' + dir + '/' + name

            # Guess mimetype
            mimetype, _ = mimetypes.guess_type(path)
            if path[-3:] == '.md':
              mimetype = 'plain/text'

            # SVG?
            if mimetype == 'image/svg+xml':
              width, height = (256, 256)
              image = cairosvg.svg2png(url=path, output_height=height, output_width=width)
              data = BytesIO(image)
              data.seek(0)
              thumbnail = base64.b64encode(data.read()).decode('utf-8')
              mimetype = 'image/png'

            # Raster image
            elif 'image/' in mimetype:
              image = Image.open(path)
              width, height = image.size
              image.thumbnail((256 , 256))
              data = BytesIO()
              image.save(data, format='PNG')
              data.seek(0)
              thumbnail = base64.b64encode(data.read()).decode('utf-8')

            # Upload file
            print('- Uploading ' + name)
            with open(path, "rb") as f:
              url = 'https://' + SERVER + '/document/' \
                  + schema + '/' + entity + '/' + str(id) + '/' + field \
                  + '/contents?access_token=' + token
              response = requests.post(url, data=f.read(), headers={ 'Content-Type': mimetype })
              oid = int(response.content)

            # Update graphQL
            query = 'mutation ($id: Int! $file:Models_DocumentTypeInputType) { data: ' \
                  + schema + '_' + entity \
                  + 'Update ( where: { id : { EQ: $id } } entity: { ' \
                  + field +': $file } ) { id } }'
            
            # Update variables
            vars = {
              'authorization': token,
              'id': int(id),
              'file': { 
                'oid': oid, 
                'type': mimetype,
                'name': name,
                'thumbnail': None
              }
            }

            # Image?
            if 'image/' in mimetype:
              vars['file']['thumbnail'] = 'data:' + mimetype + ';base64,' + thumbnail
              vars['file']['width'] = width
              vars['file']['height'] = height

            # Update
            print('- Updating ' + name)
            result = client.execute(gql(query), vars)

          except Exception as e:
            print(e)
            
# ##################################################
# Main
# ##################################################

# Directorio raíz que se desea recorrer
if __name__ == '__main__':
  folder = sys.argv[1]
  wildcard = sys.argv[2] if len(sys.argv) > 2 else '*'
  upload(folder, wildcard)
  #upload('contracts')