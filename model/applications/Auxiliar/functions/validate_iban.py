# Validate IBAN

# Import libraries
from schwifty import IBAN
import re

# Get fields
iban = TD['new']['IBAN']
if iban is None or iban == '':
  return None

# Validate IBAN
try:
  iban = re.sub(r'[^a-zA-Z0-9]', '', iban or '')
  IBAN(iban, allow_invalid=False, validate_bban=True)
  iban_ok = True
except:
  iban_ok = False
if iban_ok:
  return None
plpy.error('!!!Not a valid IBAN!!!No es un IBAN válido!!!')