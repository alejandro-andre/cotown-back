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

# Cotown includes - services
from library.services.config import settings

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Validate token
# ###################################################

def validate_token(token):

    # Get token
    if token is not None:
      g.apiClient.auth(token)
      return 0

    # Debug / Remove in production
    logger.warning('Acceso sin token')
    g.apiClient.auth(user=settings.GQLUSER, password=settings.GQLPASS)
    return 0
    #return 403