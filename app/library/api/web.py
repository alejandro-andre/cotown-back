# ###################################################
# API REST
# ---------------------------------------------------
# API for 11ty (web generation)
# ###################################################

# ###################################################
# Imports
# ###################################################

# System includes
from flask import g, request

# Cotown includes - business functions
from library.business.queries import q_flat_prices, q_room_prices, q_room_amenities

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Data endpoints for 11ty
# ###################################################

# Get flat types
def req_flats(segment, year):

   return q_flat_prices(g.dbClient, segment, year)
 
# Get room types
def req_rooms(segment, year):

   return q_room_prices(g.dbClient, segment, year)
 
# Get amenities
def req_amenities(segment):

   return q_room_amenities(g.dbClient, segment)