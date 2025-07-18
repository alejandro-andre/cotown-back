# System includes
import re
import markdown

# Cotown includes
from library.services.config import settings
from library.services.dbclient import DBClient

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Loader function
# ###################################################

def main():

  # ###################################################
  # Logging
  # ###################################################

  logger.setLevel(settings.LOGLEVEL)
  formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(module)s] [%(funcName)s/%(lineno)d] [%(levelname)s] %(message)s')
  console_handler = logging.StreamHandler()
  console_handler.setLevel(settings.LOGLEVEL)
  console_handler.setFormatter(formatter)
  logger.addHandler(console_handler)
  logger.info('Started')


  # ###################################################
  # GraphQL and DB client
  # ###################################################

  # DB API
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


  # ###################################################
  # Main
  # ###################################################

  # Get posts
  cur = dbClient.execute(con, '''SELECT id, "Rich_body", "Rich_body_en" FROM "Admin"."Email" WHERE "Name" = 'alternativas' ORDER BY id''')
  data = cur.fetchall()
  cur.close()

  # Loop thru posts
  num = 0
  for post in data:

    # Convert
    id = post['id']
    rich = markdown.markdown(post['Rich_body'])
    rich_en = markdown.markdown(post['Rich_body_en'])

    html = rich.replace('<pre class="ql-syntax" spellcheck="false">', '').replace('\n</pre>', '')
    print(html)
    break

    # Update
    sql = 'UPDATE "Admin"."Email" SET "Rich_body"=%s, "Rich_body_en"=%s WHERE id=%s'
    dbClient.execute(con, sql, (rich, rich_en, id))
    num += 1

  # Info
  con.commit()        
  logger.info('{} post processed'.format(num))


# #####################################
# Main
# #####################################

if __name__ == '__main__':

  main()
  logger.info('Finished')
