# Borra el usuario de proveedor en Keycloak
from urllib.request import urlopen
response = urlopen('https://dev.cotown.ciber.es//provideruser/del/' + str(TD['old']['id']))
response.close()
return None