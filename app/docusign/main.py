# https://account-d.docusign.com/oauth/auth?response_type=code&scope=signature%20impersonation&INTEGRATION_KEY=4c35b85f-70e7-455d-a695-01d83cac1c1e&redirect_uri=http://localhost:8080/ds/callback


from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Document, Signer, Tabs, SignHere, CustomFields, TextCustomField 
from os import path
import base64


def get_jwt_token(private_key, scopes, auth_server, client_id, impersonated_user_id):
  '''Get the jwt token'''
  api_client = ApiClient()
  api_client.set_base_path(auth_server)
  response = api_client.request_jwt_user_token(
    client_id=client_id,
    user_id=impersonated_user_id,
    oauth_host_name=auth_server,
    private_key_bytes=private_key,
    expires_in=4000,
    scopes=scopes
  )
  return response


def get_private_key(private_key_path):
  '''
  Check that the private key present in the file and if it is, get it from the file.
  In the opposite way get it from config variable.
  '''
  private_key_file = path.abspath(private_key_path)
  if path.isfile(private_key_file):
    with open(private_key_file) as private_key_file:
      private_key = private_key_file.read()
  else:
    private_key = private_key_path
  return private_key


# Constants
AUTHORIZATION_SERVER = 'account-d.docusign.com'
ACCOUNT_BASE_URI     = 'https://demo.docusign.net/restapi'
SCOPES               = ['signature', 'impersonation']
INTEGRATION_KEY      = '4c35b85f-70e7-455d-a695-01d83cac1c1e'#'4e7d683a-a230-4db9-a323-f7d87c9a5e7f'
API_ACCOUNT_ID       = '1f0de81c-2fbd-4e4c-82d5-25d87c51dc6b'#'0129c0cb-c9a4-4c0e-a070-f07c8f75559c'
IMPERSONATED_USER_ID = '750c0137-f81e-49a7-bbfb-c8850d1a5d7e'#'981ef32c-432a-41d2-8d67-70cf68131afd'
BODY                 = 'Cuerpo del email'

def main():

  # API Client setup
  api_client = ApiClient()
  api_client.set_base_path(AUTHORIZATION_SERVER)
  api_client.set_oauth_host_name(AUTHORIZATION_SERVER)
  
  # Private key
  private_key = get_private_key('private.key').encode('ascii').decode('utf-8')

  # Get JWT token
  token_response = get_jwt_token(private_key, SCOPES, AUTHORIZATION_SERVER, INTEGRATION_KEY, IMPERSONATED_USER_ID)
  auth=f'Bearer {token_response.access_token}'

  # Document
  with open('contract.pdf', 'rb') as pdf_file:
    document_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
    document = Document(
      document_base64=document_base64,
      name='Contrato de arrendamiento',
      file_extension='pdf',
      document_id='1',

    )

  # Signer
  signer = Signer(
    email='alejandro.andre@experis.es',
    name='Alejandro André',
    language='es',
    recipient_id='1',
    tabs=Tabs(
      sign_here_tabs=[
        SignHere(
          anchor_string='Fdo: Dª. Alisa Kseniia Rudova', 
          anchor_units='pixels', 
          anchor_x_offset='0', 
          anchor_y_offset='-30'
        )
      ]
    )
  )

  # Custom fields - Create first in Admin
  custom_fields = CustomFields(
    text_custom_fields=[
      TextCustomField(
        name="Booking Id",
        value="1234",
        show=True
      ),
      TextCustomField(
        name="Booking Type",
        value="B2C",
        show=True
      )
    ]
  )

  # Envelope
  envelope_definition = EnvelopeDefinition(
    documents=[document],
    recipients={'signers': [signer]},
    email_subject='Contrato de arrendamiento',
    email_blurb=BODY,
    custom_fields=custom_fields,
    status='sent'
  )

  # Send
  api_client.host = ACCOUNT_BASE_URI
  api_client.set_base_path(ACCOUNT_BASE_URI)
  api_client.set_default_header(header_name='Authorization', header_value=auth)
  envelopes_api = EnvelopesApi(api_client)
  results = envelopes_api.create_envelope(account_id=API_ACCOUNT_ID, envelope_definition=envelope_definition)
  print(results)


main()