# Borra el usuario de proveedor en Keycloak
# AFTER DELETE
from urllib.request import urlopen
response = urlopen('https://dev.cotown.ciber.es/api/v1/provideruser/del/' + str(TD['old']['id']))
response.close()
return None