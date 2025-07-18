# #####################################
# Imports
# #####################################

# External includes
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from jinja2 import Environment
from dateutil.relativedelta import relativedelta
from datetime import datetime
import smtplib
import markdown
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
      Rich_body
      Rich_body_en
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
<body style="font-family: Arial, sans-serif; font-size: 16px;">{}</body>
</html>
'''


# ######################################################
# Generate email
# ######################################################

def month(m, lang='es'):

  try:
    if lang == 'es':
      return ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'][m-1]
    else:
      return ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][m-1]
  except:
    return '--'

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
    if context.get('Customer_birth_date'):
      d = datetime.strptime(context['Customer_birth_date'], "%Y-%m-%d")
      n = datetime.now()
      edad = relativedelta(n, d)
      context['Customer_age'] = edad.years

  # Jinja environment
  env = Environment()
  env.filters['month'] = month

  # Generate subject
  text = template['Subject'] if email['Customer']['Lang'] == 'es' else template['Subject_en']
  subject = env.from_string(text).render(context)

  # Generate body from MD
  text = template['Body'] if email['Customer']['Lang'] == 'es' else template['Body_en']
  md = env.from_string(text).render(context)
  body = BASE.format(subject, markdown.markdown(md, extensions=['tables', 'attr_list']))

  # Generate body from HTML
  rich_text = template['Rich_body'] if email['Customer']['Lang'] == 'es' else template['Rich_body_en']
  rich_text = rich_text.replace('<pre class="ql-syntax" spellcheck="false">', '').replace('\n</pre>', '')
  rich_html = env.from_string(rich_text).render(context)
  rich_body = BASE.format(subject, rich_html)

  # Return
  #return subject, body
  return subject, rich_body


# ###################################################
# Send email thru SMTP
# ###################################################

def smtp_mail(to, subject, body, cc=None, bcc=None, file=None):

  # Receivers
  if settings.SMTPSEND != 1:
    return
  receivers = [to,]
  if cc:
    receivers.append(cc)
  if bcc:
    receivers.append(bcc)

  # Prepare mail
  msg = MIMEMultipart()
  msg['From']    = settings.SMTPFROM
  msg['To']      = to
  msg['Subject'] = subject
  if cc:
    msg['Cc'] = ', '.join(cc)
  msg.attach(MIMEText(body, 'html'))

  # Attach file
  if file:
    file.seek(0)
    payload = MIMEBase('application', 'octet-stream', Name=file.filename)
    payload["Content-Disposition"] = f'attachment; filename="{file.filename}"'
    payload.set_payload(file.read())
    encoders.encode_base64(payload)
    msg.attach(payload)

  # Send mail
  context = ssl.SSLContext(ssl.PROTOCOL_TLS)
  with smtplib.SMTP(settings.SMTPHOST, settings.SMTPPORT) as session:
    session.ehlo()
    session.starttls(context=context)
    session.login(settings.SMTPUSER, settings.SMTPPASS)
    errors = session.sendmail(settings.SMTPFROM, receivers, msg.as_string())
  return errors


# ###################################################
# Do one email
# ###################################################

def do_email(apiClient, email):

  # Debug
  logger.debug(email)

  # Already sent?
  if email['Sent_at'] is not None:
    return 0
    
  # Template? generate email body
  if email['Template'] is not None:
    subject, body = generate_email(apiClient, email)
    
  # Manual email?
  else:
    subject = email['Subject']
    body = markdown.markdown(email['Body'], extensions=['tables', 'attr_list']) 

  # Send email
  if subject != 'ERROR':

    # Log
    logger.debug(email['Customer']['Email'])
    logger.debug(subject)

    # ¡¡¡ Send email !!!
    smtp_mail(email['Customer']['Email'], subject, body, cc=email['Cc'], bcc=email['Cco'])

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
      'sent': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
    }

    # Call graphQL endpoint
    apiClient.call(query, variables)
    return 1
  
  return 0