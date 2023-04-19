# Borra el usuario de cliente en Keycloak
from urllib.request import urlopen
response = urlopen('https://dev.cotown.ciber.es//customeruser/del/' + str(TD['old']['id']))
response.close()
return None