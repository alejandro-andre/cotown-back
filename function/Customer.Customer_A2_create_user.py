from urllib.request import urlopen
response = urlopen('https://dev.cotown.ciber.es//customeruser/add/' + str(TD['new']['id']))
response.close()
return None