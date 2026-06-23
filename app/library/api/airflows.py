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
from library.business.queries import q_available_resources, q_booking_status, q_dashboard_operaciones, q_dashboard_lau, q_dashboard_payments, q_dashboard_deposits, q_dashboard_incasol, q_dashboard_documents, q_prev_next, q_labels, q_questionnaire, sql_dashboard_operaciones, sql_dashboard_payments, sql_dashboard_deposits, sql_dashboard_incasol, sql_dashboard_documents

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
# Document - Gets a customer document file (image/PDF)
# ---------------------------------------------------

def req_document(id, field='Document'):

  # Debug
  logger.debug('Document ' + str(id) + ' ' + field)

  # Only the document image fields are allowed
  if field not in ('Document', 'Document_back'):
    abort(404)

  # Return file
  file = g.apiClient.getFile(id, 'Customer/Customer_doc', field)
  if file.content:
    return send_file(BytesIO(file.content), mimetype=file.headers['content-type'])
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
  result = do_download(g.apiClient, g.dbClient, name, vars)
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

  if q_booking_status(g.dbClient, id, status):
    return 'ok'
  return 'ko'
 

# ---------------------------------------------------
# Gets dashboard information
# ---------------------------------------------------

def req_dashboard_lau(type=None):

  return q_dashboard_lau(g.dbClient, status=type, vars=request.args)


def req_dashboard_payments(type=None):

    return q_dashboard_payments(g.dbClient, vars=request.args)


def req_dashboard_deposits(type=None):

  return q_dashboard_deposits(g.dbClient, vars=request.args)


def req_dashboard_incasol(type=None):

  return q_dashboard_incasol(g.dbClient, vars=request.args)


def req_dashboard_operaciones(status=None):

  return q_dashboard_operaciones(g.dbClient, status=status, vars=request.args)


def req_dashboard_documents(status=None):

  return q_dashboard_documents(g.dbClient, status=status, vars=request.args)


def req_prev_next_operaciones():

  return q_prev_next(g.dbClient)


def req_dashboard_to_excel(status=None):

  # Querystring variables
  vars = {}
  for item in dict(request.args).keys():
    try:
      vars[item] = int(request.args[item])
    except:
      vars[item] = request.args[item]

  # Payments?
  if status == 'pay':
    external_sql = sql_dashboard_payments(request.args)

  # Deposits?
  elif status == 'dep':
    external_sql = sql_dashboard_deposits(request.args)

  # Incasol?
  elif status == 'inc':
    external_sql = sql_dashboard_incasol(request.args)

  # Operations
  else:
    external_sql = sql_dashboard_operaciones(status, request.args)

  # Export
  result = do_export_to_excel(g.apiClient, g.dbClient, 'dashboard.' + status, vars, external_sql)
  if result is None:
    abort(404)

  # Response
  response = send_file(result, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
  response.headers['Content-Disposition'] = 'inline; filename="dashboard.xlsx"'
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
