# Crea el usuario de proveedor en Keycloak
from urllib.request import urlopen
if TD['new']['User_name'] is not None:
   response = urlopen('https://dev.cotown.ciber.es/api/v1/provideruser/add/' + str(TD['new']['id']))
   response.close()
return None