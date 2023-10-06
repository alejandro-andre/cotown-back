# ###################################################
# Data migration
# ---------------------------------------------------
# Data migration from old CORE to new CORE
# ###################################################

# #####################################
# Imports
# #####################################

import pandas as pd
import requests


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

# #####################################
# Main
# #####################################

# Load data, csv in Excel format
print('DOCUMENTOS')
df = pd.read_csv('migration/files.in.csv', delimiter=';', encoding='utf-8')
print('Filas originales...........: ', df.shape[0])

# Process each row
for index, row in df.iterrows():

    # Ids
    email  = row['email']
    id     = row['id']
    doc_id = row['doc_id']

    # Student or booking doc
    if row['type'] == 'students':
        url = f'https://www.3kcoliving.es/backoffice/admin/students/{id}/documents/{doc_id}/download'
    else:
        url = f'https://www.3kcoliving.es/backoffice/admin/bookings/{id}/documents/download/{doc_id}'
    
    # Request
    print(url)
    response = requests.get(url)
    print(response.content)
    break
