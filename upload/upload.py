from PIL import Image
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from io import BytesIO

import base64
import mimetypes
import requests
import json
import os


SERVER = 'experis.flows.ninja'
USER   = 'modelsadmin'
PASS   = 'Ciber$2022'

def upload(folder):

  # Get token
  client = Client(transport=AIOHTTPTransport(url='https://' + SERVER + '/graphql'), fetch_schema_from_transport=True)
  result = client.execute(gql('mutation { login(username:"' + USER + '", password:"' + PASS + '") }'))
  token = result['login']

  # Upload all files
  for root, dirs, files in os.walk(folder):
    for file in files:

      # Prepare upload URL
      path = root + '\\' + file
      schema = root.split('\\')[1].split('.')
      name = file.split('_')
      id = name[0]

      # Guess mimetype
      mimetype, _ = mimetypes.guess_type(path)

      # Image?
      if 'image/' in mimetype:

        # Generate thumbnail
        image = Image.open(path)
        width, height = image.size
        image.thumbnail((256 , 256))
        thumbnail_data = BytesIO()
        image.save(thumbnail_data, format='PNG')
        thumbnail_data.seek(0)
        thumbnail_base64 = base64.b64encode(thumbnail_data.read()).decode('utf-8')

      # Upload file
      print('Uploading ' + name)
      with open(path, "rb") as f:
        url = 'https://' + SERVER + '/document/' \
            + schema[0] + '/' + schema[1] + '/' + id + '/' + schema[2] \
            + '/contents?access_token=' + token
        response = requests.post(url, data=f.read(), headers={ 'Content-Type': mimetype })
        oid = int(response.content)

      # Update graphQL
      query = 'mutation ($id: Int! $file:Models_DocumentTypeInputType) { data: ' \
            + schema[0] + '_' + schema[1] \
            + 'Update ( where: { id : { EQ: $id } } entity: { ' \
            + schema[2] +': $file } ) { id } }'
      
      # Update variables
      vars = {
        'authorization': token,
        'id': int(id),
        'file': { 
          'oid': oid, 
          'type': mimetype,
          'name': name[1] 
        }
      }

      # Image?
      if 'image/' in mimetype:
        vars['file']['thumbnail'] = 'data:' + mimetype + ';base64,' + thumbnail_base64
        vars['file']['width'] = width
        vars['file']['height'] = height

      # Update
      print('Updating ' + name)
      result = client.execute(gql(query), vars)


# Directorio raíz que se desea recorrer
upload('files')