# ###################################################
# API REST
# ---------------------------------------------------
# Security functions
# ###################################################

# ###################################################
# Imports
# ###################################################

# System includes
from flask import g
from cachetools import TTLCache

# Cotown includes - services
from library.services.config import settings

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Cache
# ###################################################

cache = TTLCache(maxsize=100, ttl=60)


# ###################################################
# Validate token
# ###################################################

def validate_token(token):

   # Check cache first
   if token in cache:
       return cache[token]

   # Forbidden by default
   result = 403

   # Call API to check if token is valid
   if token is not None:
     try:
       g.apiClient.auth(token)
       data = g.apiClient.call('{ user: getCurrentUser { currentUser } }')
       if data['user']['currentUser'] != 'anonymous':
         result = 0
     except:
       pass
     cache[token] = result
     return result

   # Debug / Remove in production
   g.apiClient.auth(user=settings.GQLUSER, password=settings.GQLPASS)
   logger.warning('Acceso sin token')
   result = 0

   # Forbidden
   return result