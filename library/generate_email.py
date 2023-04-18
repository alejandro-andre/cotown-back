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
# Query to retrieve the email template
# ######################################################

TEMPLATE = '''
query EmailByCode ($code: String!) {
    data: Auxiliar_EmailList (
        where: { Name: { EQ: $code } }
    ) { 
      Name
      Subject
      Body
      Query
    }
}'''


# ######################################################
# Generate email
# ######################################################

def do_email(apiClient, email):

  # Template and entity id
  id = email['Entity_id']
  variables = { 'code': email['Template'].lower() }
  result = apiClient.call(TEMPLATE, variables)
  if len(result['data']) == 0:
      return 'ERROR', 'ERROR'
  template = flatten_json(result['data'][0])

  # Context
  context = email

  # Call graphQL endpoint
  if id is not None and template['Query'] != '':
    result = apiClient.call(template['Query'], {'id': id})
    context |= flatten_json(result['data'][0])

  # Jinja environment
  env = Environment()

  # Generate subject
  text = template['Subject']
  subject = env.from_string(text).render(context)

  # Generate body
  text = template['Body']
  body = env.from_string(text).render(context)

  # Return
  return subject, body
