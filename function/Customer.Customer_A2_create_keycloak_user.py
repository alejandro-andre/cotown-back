# Crea el usuario de cliente en Keycloak
from urllib.request import urlopen
if TD['new']['User_name'] is not None:
    response = urlopen('https://dev.cotown.ciber.es//customeruser/add/' + str(TD['new']['id']))
    response.close()
return None