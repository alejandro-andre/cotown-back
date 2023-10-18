# ###################################################
# Data migration
# ---------------------------------------------------
# Data migration from old CORE to new CORE
# ###################################################

# #####################################
# Imports
# #####################################

# System includes
from PIL import Image
from io import BytesIO
import pandas as pd
import mimetypes
import base64
import requests

from pillow_heif import register_heif_opener
register_heif_opener()

# Cotown includes
from library.services.config import settings
from library.services.apiclient import APIClient


# #####################################
# Query
# #####################################

'''
Backoffice:
https://www.3kcoliving.es/backoffice/login
dalarcon@cotown.com
l3$MjE1VHQ69

Base de datos:
https://3kcoliving.es/phpmyadmin/
vanguardstudenthousing
5vA*7aJouT8%
myvanguardstudenthousing
Qi80#GW1AA7N
 
-- Documents
SELECT u.email as "email", 'students' as "type", u.id as "id", dt.id as "doc_id", d.path as "path"
FROM documents d
INNER JOIN document_types dt ON dt.id = d.type_id
INNER JOIN users u ON u.id = d.user_id
WHERE user_id IS NOT NULL
UNION
SELECT rq.email as "email", 'bookings' as "type", d.booking_id as "id", dt.id as "doc_id", d.path as "path"
FROM documents d
INNER JOIN document_types dt ON dt.id = d.type_id
INNER JOIN bookings b on b.id = d.booking_id
INNER JOIN requests r on b.request_id = r.id
INNER JOIN requesters rq on rq.id = r.requester_id
WHERE d.booking_id IS NOT NULL
ORDER BY 1, 2;

https://www.3kcoliving.es/backoffice/admin/bookings/1065/documents/download/2
https://www.3kcoliving.es/backoffice/admin/students/1358/documents/2/download
'''

# Old CORE
# 1: Front ID
# 2: Back ID
# 3: Registration ¿?
# 4: SEPA

# New CORE
# 1: DNI/NIF
# 2: NIE
# 3: Id Nacional
# 4: Pasaporte
# 6: Matrícula
# 9: SEPA


# #####################################
# Add document
# #####################################

def add_doc(index, type_id, customer_id, filepath_front, filepath_back):

    print(index, type_id, customer_id, filepath_front, filepath_back)

    # File data
    mimetype_front = ''
    mimetype_back = ''
    if filepath_front:
        mimetype_front, _ = mimetypes.guess_type('../migration/' + filepath_front)
    if filepath_back:
        mimetype_back, _ = mimetypes.guess_type('../migration/' + filepath_back)
    print(mimetype_front, mimetype_back)

    # Thumbnail
    thumbnail_front = ''
    thumbnail_back = ''
    if filepath_front and 'image/' in mimetype_front:
        image = Image.open('../migration/' + filepath_front)
        width_fromt, height_front = image.size
        image.thumbnail((256 , 256))
        bio = BytesIO()
        image.save(bio, format='PNG')
        bio.seek(0)
        thumbnail_front = base64.b64encode(bio.read()).decode('utf-8')
    if filepath_back and 'image/' in mimetype_back:
        image = Image.open('../migration/' + filepath_back)
        width_back, height_back = image.size
        image.thumbnail((256 , 256))
        bio = BytesIO()
        image.save(bio, format='PNG')
        bio.seek(0)
        thumbnail_back = base64.b64encode(bio.read()).decode('utf-8')

    # Open file
    oid_front = 0
    oid_back = 0
    if filepath_front:
        with open('../migration/' + filepath_front, 'rb') as file:
            url = 'https://' + apiClient.server + '/document/Customer/Customer_doc/' + str(index + 1) + '/' + 'Document/contents?access_token=' + apiClient.token
            response = requests.post(url, data=file.read(), headers={ 'Content-Type': mimetype_front })
            oid_front = int(response.content)

    if filepath_back:
        with open('../migration/' + filepath_back, 'rb') as file:
            url = 'https://' + apiClient.server + '/document/Customer/Customer_doc/' + str(index + 1) + '/' + 'Document_back/contents?access_token=' + apiClient.token
            response = requests.post(url, data=file.read(), headers={ 'Content-Type': mimetype_front })
            oid_back = int(response.content)

    # Insert query
    query = '''
        mutation ($cid: Int! $tid: Int! $file_front: Models_DocumentTypeInputType $file_back: Models_DocumentTypeInputType) {
            data: Customer_Customer_docCreate (
                entity: {
                    Customer_id: $cid
                    Customer_doc_type_id: $tid
                    Document: $file_front
                    Document_back: $file_back
                }
            ) { 
                id 
            }
        }'''

    # Variables
    vars = {
        'authorization': apiClient.token,
        'cid': int(customer_id),
        'tid': int(type_id)
    }
    if filepath_front:
        vars['file_front'] = { 
            'oid': oid_front, 
            'type': mimetype_front,
            'name': filepath_front.split('/')[-1],
            'thumbnail': 'data:' + mimetype_front + ';base64,' + thumbnail_front if thumbnail_front != '' else None
        }
    if filepath_back:
        vars['file_back'] = { 
            'oid': oid_back, 
            'type': mimetype_back,
            'name': filepath_back.split('/')[-1],
            'thumbnail': 'data:' + mimetype_back + ';base64,' + thumbnail_back if thumbnail_back != '' else None
        }

    # Insert record
    #print(vars)
    try:
        apiClient.call(query, vars)
    except Exception as e:
        print(e)


# #####################################
# Main
# #####################################

# graphQL API
apiClient = APIClient(settings.SERVER)
apiClient.auth(user=settings.GQLUSER, password=settings.GQLPASS)

# Load data, csv in Excel format
print('DOCUMENTOS')
pd.options.display.max_columns = 0
df = pd.read_csv('../migration/files.in.csv', delimiter=';', encoding='utf-8')
print('Filas originales...........: ', df.shape[0])

# Group by email
df = df.groupby(['email', 'doc_id'])['path'].first().reset_index()
df['aux'] = 'doc_' + df['doc_id'].astype(str)

# Pivot doc types
df = df.pivot(index='email', columns='aux', values='path').reset_index()
df = df.where(pd.notna(df), None)
print('Emails distintos...........: ', df.shape[0])

# Process each row
ecount = 0
dcount = 0
for index, row in df.iterrows():

    # Get customer
    data = apiClient.call('''
    query Customer ($email: String) {
        data: Customer_CustomerList ( where: { Email: { EQ: $email} } ) {
            id
            Id_type_id 
            Email
        }
    }
    ''', { 'email': row['email'] })

    # Path
    if len(data['data']) > 0:

        if index < 41:
            continue

        # Customer data
        customer = data['data'][0]
        ecount += 1

        # Document type
        if row['doc_1'] or row['doc_2']:
            type_id = customer['Id_type_id']
            add_doc(index, type_id, customer['id'], row['doc_1'], row['doc_2'])
            dcount += 1

        if row['doc_3']:
            type_id = 6
            add_doc(index, type_id, customer['id'], row['doc_3'], None)
            dcount += 1

        if row['doc_4']:
            print(row['doc_4'])
            type_id = 9
            add_doc(index, type_id, customer['id'], row['doc_4'], None)
            dcount += 1

print('Emails procesados..........: ', ecount)
print('Documentos procesados......: ', dcount)