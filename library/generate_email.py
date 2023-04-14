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

  # Template
  template = email['Template'].lower()

  # Entity id
  id = int(email.get('Entity_id', 0))
  id = 900

  # Context
  context = email

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

  print(email['Customer']['Email'])
  print(subject)
  print(body)

  # Return
  return subject, body
