# ######################################################
# Imports
# ######################################################

from docxtpl import DocxTemplate
from io import BytesIO
import jinja2
import datetime


# ######################################################
# Additional functions
# ######################################################

def month(m):

  return ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'][m]


def part(p):

  s = ''
  part = [
    '', '', 'media', 'tercera', 'cuarta', 'quinta', 'sexta', 'septima', 'octava', 'novena', 'décima', 'onceava', 'doceava', 'treceava'
  ][int(p[2:])]
  n, s = ('una ', '') if p[0] == '1' else ('dos ', 's')
  return n + part + s + ' parte' + s +' (' + p + ' parte' + s + ')'


# ######################################################
# Flatten JSON
# ######################################################

def flatten_json(json_obj, key='', flattened=None, prefix=''):

  # Empty json, create empty result
  if flattened is None:
    flattened = {}

  # Dictionary, get every key, and flatten each item
  if isinstance(json_obj, dict):
    for key, value in json_obj.items():
      new_prefix = f"{prefix}.{key}" if prefix else key
      flatten_json(value, key, flattened, new_prefix)

  # List, keep the list flattening each element
  elif isinstance(json_obj, list):
    array = []
    for i, value in enumerate(json_obj):
      array.append(flatten_json(value))
    flattened[key] = array

  # Scalar, store item
  else:
    flattened[key] = json_obj

  return flattened


# ######################################################
# Generate document
# ######################################################

def generate_doc(context, template):

  # Prepare render context
  now = datetime.datetime.now()
  context = flatten_json(context)
  context['Today_day'] = now.day
  context['Today_month'] = now.month
  context['Today_year'] = now.year

  # Add custom functions
  jinja_env = jinja2.Environment()
  jinja_env.filters['month'] = month
  jinja_env.filters['part'] = part

  # Render contract
  doc = DocxTemplate(template)
  doc.render(context, jinja_env)

  # Convert to bytes
  file = BytesIO()
  doc.save(file)
  file.seek(0)
  return file