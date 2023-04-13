# #####################################
# Imports
# #####################################

# External includes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl

# Logging
import logging
logger = logging.getLogger('COTOWN')


# ###################################################
# Constants
# ###################################################

HOST = 'smtp.office365.com'
PORT = '587'
FROM = 'no-replay@cotown.com'
USER = 'no-replay@cotown.com'
PASS = 'Suq97716'


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
