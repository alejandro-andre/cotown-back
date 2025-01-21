# ###################################################
# API REST
# ---------------------------------------------------
# API access for Airflows buttons and logic
# ###################################################

# ###################################################
# Imports
# ###################################################

# System includes
from flask import g, request, abort, send_file, redirect
from io import BytesIO

# Cotown includes - business functions
from library.business.export import do_export_to_excel
from library.business.occupancy import do_occupancy
from library.business.download import do_download
from library.business.queries import q_available_resources, q_booking_status, q_dashboard_operaciones, q_dashboard_lau, q_prev_next, q_labels, q_questionnaire, sql_dashboard_operaciones

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Airflows plugins
# ###################################################

# ---------------------------------------------------
# Href - Redirects
# ---------------------------------------------------

def req_href(path):

  return redirect(path, code=302)


# ---------------------------------------------------
# Signature - Gets the signature image for the contracts
# ---------------------------------------------------

def req_signature(id):

  # Debug
  logger.debug('Signature ' + str(id))

  # Return image
  image = g.apiClient.getFile(id, 'Provider/Provider_contact', 'Signature')
  if image.content:
    return send_file(BytesIO(image.content), mimetype=image.headers['content-type'])
  abort(404)


# ---------------------------------------------------
# Download files (PDFs) in ZIP format - Contracts, bills...
# ---------------------------------------------------

def req_download(name):

  # Debug
  logger.debug('Download ' + name)

  # Querystring variables
  vars = {}
  for item in dict(request.args).keys():
    try:
      vars[item] = int(request.args[item])
    except:
      vars[item] = request.args[item]

  # Download zip
  result = do_download(g.apiClient, name, vars)
  if result is None:
    abort(404)

  # Response
  response = send_file(result, mimetype='application/zip')
  response.headers['Content-Disposition'] = 'inline; filename="' + name + '.zip"'
  return response
 

# ---------------------------------------------------
# Export data (queries) to excel
# ---------------------------------------------------

def req_export(name):

  # Debug
  logger.debug('Export ' + name)
  if name == 'occupancy':
    return req_occupancy()

  # Querystring variables
  vars = {}
  for item in dict(request.args).keys():
    try:
      vars[item] = int(request.args[item])
    except:
      vars[item] = request.args[item]

  # Export
  result = do_export_to_excel(g.apiClient, g.dbClient, name, vars)
  if result is None:
    abort(404)

  # Response
  response = send_file(result, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
  response.headers['Content-Disposition'] = 'inline; filename="' + name + '.xlsx"'
  return response   
       

# ---------------------------------------------------
# Occupancy report
# ---------------------------------------------------

def req_occupancy():

  # Querystring variables
  vars = {}
  for item in dict(request.args).keys():
    try:
      vars[item] = int(request.args[item])
    except:
      vars[item] = request.args[item]

  result = do_occupancy(g.dbClient, vars)
  if result is None:
    abort(404)

  # Response
  response = send_file(result, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
  response.headers['Content-Disposition'] = 'inline; filename="occupancy.xlsx"'
  return response   


# ---------------------------------------------------
# Available resources for planning
# ---------------------------------------------------

def req_availability():
   
  data = request.get_json()
  result = q_available_resources(
    g.dbClient,
    date_from=data.get('date_from'),
    date_to=data.get('date_to'),
    building=data.get('building', ''),
    flat_type=data.get('flat_type', ''),
    place_type=data.get('place_type', '')
  )
  if result is None:
    return {}
  return result


# ---------------------------------------------------
# Change booking status (booking button)
# ---------------------------------------------------

def req_booking_status(id, status, oldstatus=None):

  if status == 'descartada':
    if oldstatus in ('solicitud','alternativas','pendientepago'):
      pass
    elif oldstatus in ('solicitudpagada', 'alternativaspagada'):
      status = 'descartadapagada'
    else:
      return 'ok'

  if q_booking_status(g.dbClient, id, status):
    return 'ok'
  return 'ko'
 

# ---------------------------------------------------
# Gets dashboard information
# ---------------------------------------------------

def req_dashboard_lau(type=None):

  return q_dashboard_lau(g.dbClient, status=type, vars=request.args)


def req_dashboard_operaciones(status=None):

  return q_dashboard_operaciones(g.dbClient, status=status, vars=request.args)


def req_prev_next_operaciones():

  return q_prev_next(g.dbClient)


def req_report_operaciones(status=None):

  # Querystring variables
  vars = {}
  for item in dict(request.args).keys():
    try:
      vars[item] = int(request.args[item])
    except:
      vars[item] = request.args[item]

  # Export
  external_sql = sql_dashboard_operaciones(status, request.args)
  result = do_export_to_excel(g.apiClient, g.dbClient, 'operaciones.' + status, vars, external_sql)
  if result is None:
    abort(404)

  # Response
  response = send_file(result, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
  response.headers['Content-Disposition'] = 'inline; filename="operaciones.xlsx"'
  return response   



# ---------------------------------------------------
# Gets labels for translations
# ---------------------------------------------------

def req_labels(id, locale):

  return q_labels(g.dbClient, id, locale)

# ---------------------------------------------------
# Saves answers to questionnaires
# ---------------------------------------------------

def req_questionnaire(id):

  # Get answers
  answers = request.get_json()
  values = []
  for group in answers['questions']:
    for question in group['questions']:
      values.append((id, question['id'], str(question['value']),))

  # Insert answers
  return q_questionnaire(g.dbClient, id, values, answers.get('issues'))
