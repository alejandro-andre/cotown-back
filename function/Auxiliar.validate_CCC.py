# Validate IBAN/SWIFT

# Import libraries
from schwifty import IBAN
import re

# Get fields
iban = TD['new']['Bank_account']
swift = TD['new']['Swift']
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

# SWIFT required
if swift is None:
  plpy.error('!!!Bank account not a valid IBAN, SWIFT code required!!!La cuenta no es un IBAN válido, se requiere el codigo SWIFT !!!')
  
# Validate SWIFT
swift = re.sub(r'[^a-zA-Z0-9]', '', swift or '')
regex = '^[A-Z]{4}[-]{0,1}[A-Z]{2}[-]{0,1}[A-Z0-9]{2}[-]{0,1}([0-9]{3})?$'
swift_ok = re.search(regex, swift) is not None
if not swift_ok:
  plpy.error('!!!SWIFT code not valid!!!Codigo SWIFT no válido!!!')

# Ok  
return None