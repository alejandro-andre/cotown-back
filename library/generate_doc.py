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

  if p is None:
    return

  try:  
    s = ''
    part = [
      '', '', 'media', 'tercera', 'cuarta', 'quinta', 'sexta', 'septima', 'octava', 'novena', 'décima', 'onceava', 'doceava', 'treceava', 'catorceava', 'quinceava'
    ][int(p[2:])]
    n, s = ('una ', '') if p[0] == '1' else ('dos ', 's')
    return n + part + s + ' parte' + s +' (' + p + ' parte' + s + ')'
  except Exception as error:
    print(p, error)
    return p


# ######################################################
# Generate document
# ######################################################

def generate_doc(context, template):

  # Prepare render context
  now = datetime.datetime.now()
  context['Today_day'] = now.day
  context['Today_month'] = now.month
  context['Today_year'] = now.year

  # Add custom functions
  jinja_env = jinja2.Environment()
  jinja_env.filters['month'] = month
  jinja_env.filters['part'] = part

  # Render contract
  doc = DocxTemplate(BytesIO(template))
  doc.render(context, jinja_env)

  # Convert to bytes
  file = BytesIO()
  doc.save(file)
  file.seek(0)
  return file