# ###################################################
# Batch process
# ---------------------------------------------------
# Calculates resource weights
# ###################################################

# ###################################################
# Imports
# ###################################################


# Cotown includes
from library.services.config import settings
from library.services.dbclient import DBClient

# Logging
import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger('COTOWN')

# Date
from datetime import date


# ###################################################
# Helpers
# ###################################################

def round_to_100(raw):
  '''Round a group of percentages (dict key -> value, summing ~100) to 2 decimals
  while keeping the group total unchanged, distributing the rounding remainder
  to the largest fractions (largest remainder method). Ties are broken by key so
  the result is deterministic even when several remainders are equal.'''
  units = {k: v * 100 for k, v in raw.items()}
  parents = {k: int(u) for k, u in units.items()}
  deficit = round(sum(units.values())) - sum(parents.values())
  order = sorted(units, key=lambda k: (-(units[k] - parents[k]), k))
  for k in order[:max(deficit, 0)]:
    parents[k] += 1
  return {k: parents[k] / 100 for k in raw}


# ###################################################
# Main function
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
  file_handler = RotatingFileHandler('log/batch_law.log', maxBytes=1000000, backupCount=5)
  file_handler.setLevel(settings.LOGLEVEL)
  file_handler.setFormatter(formatter)
  logger.addHandler(console_handler)
  logger.addHandler(file_handler)
  logger.info('Started')


  # ###################################################
  # DB client
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

  # Get year (if September or later, use next year)
  today = date.today()
  year = today.year + 1 if today.month >= 9 else today.year

  # Get resources not CTH locked today
  cur_read = dbClient.execute(con, f'''
    SELECT
      r."Code" AS "Resource",
      rpt."Code" AS "Place_type",
      r."Resource_type" AS "Type",
      r."Weigth" AS "Weight",
      pr."Multiplier" * (pd."Rent_long" + pd."Rent_medium") / 2 AS "Price",
      NOT EXISTS (
        SELECT 1 FROM "Resource"."Resource_availability" ra
        WHERE ra."Resource_id" = r.id AND ra."Status_id" = 5
          AND COALESCE(ra."Date_from", CURRENT_DATE) <= CURRENT_DATE
          AND COALESCE(ra."Date_to", CURRENT_DATE) >= CURRENT_DATE
      ) AS "Available"
    FROM "Resource"."Resource" r
      LEFT JOIN "Resource"."Resource_place_type" rpt ON rpt.id = r."Place_type_id"
      LEFT JOIN "Billing"."Pricing_rate" pr ON pr.id = r."Rate_id"
      LEFT JOIN "Billing"."Pricing_detail" pd ON pd."Year" = {year} AND pd."Building_id" = r."Building_id" AND pd."Flat_type_id" = r."Flat_type_id" AND (pd."Place_type_id" = r."Place_type_id" OR pd."Place_type_id" IS NULL)
    WHERE r."Resource_type" IN ('piso', 'habitacion', 'plaza')
    ORDER BY r."Code" ASC
  ''')
  resources = cur_read.fetchall()
  cur_read.close()

  # Building is the first 6 characters of the resource code
  def building_of(resource):
    return resource[:6]

  # Flat is the first 12 characters of the resource code
  def flat_of(resource):
    return resource[:12]

  # Price per resource (unavailable resources do not count, their price is ignored)
  resource_prices = {}
  for resource, place_type, rtype, current_weight, price, available in resources:
    resource_prices[resource] = (price or 0) if available else 0

  # Availability per resource
  availability = {r: av for (r, pt, rt, cw, pr, av) in resources}

  # Plazas grouped by their habitacion (a plaza code is "<habitacion>.<suffix>")
  habitacion_codes = {r for (r, pt, rt, cw, pr, av) in resources if rt == 'habitacion'}
  plazas_by_room = {}
  for r, pt, rt, cw, pr, av in resources:
    if rt == 'plaza':
      parent = r.rsplit('.', 1)[0]
      if parent in habitacion_codes:
        plazas_by_room.setdefault(parent, []).append(r)
  rooms_with_plazas = set(plazas_by_room)

  # A leaf is a plaza or an individual habitacion (one without plazas)
  def is_leaf(resource, rtype):
    return rtype == 'plaza' or (rtype == 'habitacion' and resource not in rooms_with_plazas)

  # Leaf price per flat and per building.
  # A habitacion with plazas is not a leaf; its plazas are counted instead (its own price is discarded).
  flat_prices = {}
  for resource, place_type, rtype, current_weight, price, available in resources:
    if is_leaf(resource, rtype):
      flat = flat_of(resource)
      flat_prices[flat] = flat_prices.get(flat, 0) + resource_prices[resource]

  building_prices = {}
  for flat, total in flat_prices.items():
    building = building_of(flat)
    building_prices[building] = building_prices.get(building, 0) + total

  # Weights as percentages, rounded per group so each group's total stays exactly 100.00
  weights = {}

  # Unavailable resources (CTH block covering today) weigh 0
  for resource, place_type, rtype, current_weight, price, available in resources:
    if not available:
      weights[resource] = 0

  # Leaves of each flat (plazas + individual habitaciones) -> sum to 100 per flat
  leaves_by_flat = {}
  for resource, place_type, rtype, current_weight, price, available in resources:
    if available and is_leaf(resource, rtype):
      total = flat_prices.get(flat_of(resource), 0)
      if total and resource_prices[resource]:
        leaves_by_flat.setdefault(flat_of(resource), {})[resource] = resource_prices[resource] / total * 100
  for raw in leaves_by_flat.values():
    weights.update(round_to_100(raw))

  # A habitacion with plazas weighs the exact sum of its plazas' rounded weights
  for room, plazas in plazas_by_room.items():
    if availability.get(room):
      weights[room] = round(sum(weights.get(p, 0) for p in plazas), 2)

  # Pisos of each building -> sum to 100 per building
  pisos_by_building = {}
  for resource, place_type, rtype, current_weight, price, available in resources:
    if available and rtype == 'piso':
      total = building_prices.get(building_of(resource), 0)
      numerator = flat_prices.get(flat_of(resource), 0)
      if total and numerator:
        pisos_by_building.setdefault(building_of(resource), {})[resource] = numerator / total * 100
  for raw in pisos_by_building.values():
    weights.update(round_to_100(raw))

  # Prepare the weight updates, only where the weight has changed (not executed)
  num = 0
  for resource, place_type, rtype, current_weight, price, available in resources:
    if resource not in weights:
      continue
    new_weight = weights[resource]
    old_weight = round(float(current_weight), 2) if current_weight is not None else None
    if 'BLM335' in resource:
      logger.info(f'{resource}: {old_weight} -> {new_weight}')
    if new_weight != old_weight:
      num += 1
      logger.info('UPDATE "Resource"."Resource" SET "Weigth" = {} WHERE "Code" = \'{}\'  -- was {}'.format(new_weight, resource, old_weight))

  # Write cursor
  cur_write = con.cursor()

  # Commit
  con.commit()
  cur_write.close()
  logger.info('{} resources processed'.format(num))


# #####################################
# Main
# #####################################

if __name__ == '__main__':

  main()
  logger.info('Finished')
