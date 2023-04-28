# #####################################
# Imports
# #####################################

# External includes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment 
import smtplib
import ssl
import logging

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Cotown includes
from library.services.utils import flatten_json


# ###################################################
# Constants
# ###################################################

HOST = 'smtp.office365.com'
PORT = '587'
FROM = 'no-replay@cotown.com'
USER = 'no-replay@cotown.com'
PASS = 'Suq97716'


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
# Base template for HTML
# ######################################################

BASE = '''
<html>
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
</head>
<body  style="font-family: Arial, sans-serif; font-size: 16px;">{}</body>
</html>
'''


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
  body = BASE.format(env.from_string(text).render(context))

  # Return
  return subject, body


# ###################################################
# Send email thru SMTP
# ###################################################

def smtp_mail(to, subject, body):

    # Receivers
    receivers = [to,]

    # Prepare mail
    msg = MIMEMultipart()
    msg['From']    = FROM
    msg['To']      = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    # Send mail
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    session = smtplib.SMTP(HOST, PORT)
    session.ehlo()
    session.starttls(context=context)
    session.login(USER, PASS)
    errors = session.sendmail(FROM, receivers, msg.as_string())
    session.quit()
    return errors