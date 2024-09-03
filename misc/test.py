from library.services.dbclient import DBClient
from library.services.config import settings

dbClient = DBClient(
    host=settings.SERVER,
    port=settings.get('DBPORT', 5432),
    dbname=settings.DATABASE,
    user=settings.DBUSER,
    password=settings.DBPASS,
    sshuser=settings.SSHUSER,
    sshpassword=settings.get('SSHPASS', None),
    sshprivatekey=settings.get('SSHPKEY', None)
)
dbClient.connect()

con = dbClient.getconn()
cur = dbClient.execute(con,'SELECT * FROM "Booking"."Booking" LIMIT 1')

columnas = cur.description
for col in columnas:
    cur.execute("SELECT typname FROM pg_type WHERE oid = %s;", (col.type_code,))
    type_name = cur.fetchone()
    print(f'{col.name}, {col.type_code}, {type_name[0]}')

cur.close()
dbClient.putconn(con)