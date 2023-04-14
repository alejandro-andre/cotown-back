# ######################################################
# Imports
# ######################################################

# System includes
import logging
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Cotown includes
from library.utils import flatten_json


# ######################################################
# Generate email
# ######################################################

def do_email(apiClient, email):

  # Template and entity id
  template = email['Template'].lower()
  id = email['Entity_id']

  # Context
  context = email
  if id is not None:
    try:

      # Get query, if exists
      fi = open('templates/email/' + template + '.graphql', 'r')
      query = fi.read()
      fi.close()

      # Call graphQL endpoint
      result = apiClient.call(query, {'id': id})
      context |= flatten_json(result['data'][0])

    except:
      pass

  # Jinja environment
  env = Environment(
      loader=FileSystemLoader('./templates/email'),
      autoescape=select_autoescape(['html', 'xml'])
  )

  # Generate subject
  tpl = env.get_template(template + '.subject')
  subject = tpl.render(context)

  # Generate body
  tpl = env.get_template(template + '.body')
  body = tpl.render(context)

  # Return
  return subject, body
