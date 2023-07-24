# #####################################
# Imports
# #####################################

# External includes
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from jinja2 import Environment 
import smtplib
import markdown
import datetime
import ssl
import logging

# Logging
import logging
logger = logging.getLogger('COTOWN')

# Cotown includes
from library.services.config import settings
from library.services.utils import flatten


# ######################################################
# Query to retrieve the email template
# ######################################################

TEMPLATE = '''
query EmailByCode ($code: String!) {
    data: Admin_EmailList (
        where: { Name: { EQ: $code } }
    ) { 
      Name
      Subject
      Subject_en
      Body
      Body_en
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
<title>{}</title>
</head>
<body  style="font-family: Arial, sans-serif; font-size: 16px;">{}</body>
</html>
'''


# ######################################################
# Generate email
# ######################################################

def generate_email(apiClient, email):

  # Template and entity id
  id = email['Entity_id']
  variables = { 'code': email['Template'].lower() }
  result = apiClient.call(TEMPLATE, variables)
  if len(result['data']) == 0:
      return 'ERROR', 'ERROR'
  template = flatten(result['data'][0])

  # Context
  context = email

  # Call graphQL endpoint
  if id is not None and template['Query'] != '':
    result = apiClient.call(template['Query'], {'id': id})
    context |= flatten(result['data'][0])

  # Jinja environment
  env = Environment()

  # Generate subject
  text = template['Subject'] if email['Customer']['Lang'] == 'es' else template['Subject_en']
  subject = env.from_string(text).render(context)

  # Generate body
  text = template['Body'] if email['Customer']['Lang'] == 'es' else template['Body_en']
  md = env.from_string(text).render(context)
  body = BASE.format(subject, markdown.markdown(md, extensions=['tables', 'attr_list']))

  # Return
  return subject, body


# ###################################################
# Send email thru SMTP
# ###################################################

def smtp_mail(to, subject, body, file=None):

    # Receivers
    receivers = [to,]

    # Prepare mail
    msg = MIMEMultipart()
    msg['From']    = settings.SMTPADDR
    msg['To']      = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    # Attach file
    if file:
      payload = MIMEBase('application', 'octate-stream', Name=file.filename)
      payload["Content-Disposition"] = f'attachment; filename="{file.filename}"'
      payload.add_header('Content-Decomposition', 'attachment', filename=file.filename)
      payload.set_payload(file.read())
      encoders.encode_base64(payload)
      msg.attach(payload)

    # Send mail
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    session = smtplib.SMTP(settings.SMTPHOST, settings.SMTPPORT)
    session.ehlo()
    session.starttls(context=context)
    session.login(settings.SMTPUSER, settings.SMTPPASS)
    errors = session.sendmail(settings.SMTPFROM, receivers, msg.as_string())
    session.quit()
    return errors


# ###################################################
# Do one email
# ###################################################

def do_email(apiClient, email):

    # Debug
    logger.debug(email)

    # Already sent?
    if email['Sent_at'] is not None:
      return
      
    # Template? generate email body
    if email['Template'] is not None:
      subject, body = generate_email(apiClient, email)
      
    # Manual email?
    else:
      subject = email['Subject']
      body = markdown.markdown(email['Body'], extensions=['tables', 'attr_list'])  

    # Update query
    query = '''
    mutation ($id: Int! $subject: String! $body: String! $sent: String!) {
      Customer_Customer_emailUpdate (
        where:  { id: {EQ: $id} }
        entity: { 
          Subject: $subject 
          Body: $body
          Sent_at: $sent
        }
      ) { id }
    }
    '''

    # Update variables
    variables = {
      'id': email['id'], 
      'subject': subject,
      'body': body,
      'sent': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
    }

    # Call graphQL endpoint
    apiClient.call(query, variables)

    # Debug
    if '@test.com' in email['Customer']['Email']:
        return

    # Send email
    if subject != 'ERROR':
      logger.debug(email['Customer']['Email'])
      logger.debug(subject)
      logger.debug(body)
      smtp_mail(email['Customer']['Email'], subject, body)