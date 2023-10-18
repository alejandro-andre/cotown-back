# ###################################################
# Clean OIDs
# ###################################################

# #####################################
# Imports
# #####################################

# Cotown includes
from library.services.config import settings
from library.services.dbclient import DBClient


# #####################################
# Main
# #####################################

# DB API
dbClient = DBClient(
  host=settings.SERVER, 
  dbname=settings.DATABASE, 
  user=settings.DBUSER, 
  password=settings.DBPASS,
  sshuser=settings.SSHUSER, 
  sshpassword=settings.get('SSHPASS', None),
  sshprivatekey=settings.get('SSHPKEY', None)
)
dbClient.connect()

# Load existing oids
dbClient.select('SELECT oid FROM pg_largeobject_metadata;')
db_oids = set([item[0] for item in dbClient.fetchall()])

# Get fields of type DOCUMENT
dbClient.select('''
  select ea.name, e."schema", e."name" 
  from "Models"."EntityAttribute" ea
  inner join "Models"."Entity" e on ea.container = e.id
  where ea.type = 'DOCUMENT'
''')
fields = dbClient.fetchall()

# Add metamodel fields
fields.append(['customerLogo', 'Models', 'Personalization'])
fields.append(['template', 'Models', 'Report'])
fields.append(['package', 'Models', 'WebPackage'])

# All oids in the tables of the model
model_oids = set()

# Get oids from each field
for item in fields:

  field = item[0]
  schema = item[1]
  table = item[2]
  print(schema, table, field, end=': ')

  # Get oids
  dbClient.select(f'''
    select ("{field}").oid
    from "{schema}"."{table}" t
    where ("{field}").oid is not null
  ''')
  oids = [item[0] for item in dbClient.fetchall()]
  print(len(oids))

  # Add them to global set
  if len(oids):
    model_oids.update(oids)

# Orphan oids
orphan = list(db_oids - model_oids)
errors = list(model_oids - db_oids)

# Result
print()
print(len(model_oids))
print(len(db_oids))
print(len(orphan))
print(len(errors))
print()

# Unlink (test)
for index, oid in enumerate(sorted(orphan)):
  print(oid)
  dbClient.execute(f'select lo_unlink({oid})''')
  if index % 100 == 0:
    dbClient.commit()

# End
dbClient.commit()
dbClient.disconnect()