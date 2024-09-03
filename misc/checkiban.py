from schwifty import IBAN, exceptions
import re

with open('iban.csv', 'r') as f:
    for line in f:
        if 'str' in line:
           break
        try:
            code = re.sub(r'[^a-zA-Z0-9]', '', line)
            iban = IBAN(line, allow_invalid=False, validate_bban=True)
            print(iban.is_valid, iban.bic if iban.bic else '--------', iban.formatted, iban.bank_name)
        except exceptions.InvalidLength as ist:
            print('Longitud inválida')
        except exceptions.InvalidStructure as ist:
            print('Estructura inválida')
        except exceptions.InvalidChecksumDigits as ist:
            print('Checksum incorrecto')
        except Exception as ex:
            print('Error:', ex)

f.close()