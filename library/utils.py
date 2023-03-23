# ######################################################
# Flatten JSON
# ######################################################

def flatten_json(json_obj, key='', flattened=None, prefix=''):

  # Empty json, create empty result
  if flattened is None:
    flattened = {}

  # Dictionary, get every key, and flatten each item
  if isinstance(json_obj, dict):
    for key, value in json_obj.items():
      new_prefix = f"{prefix}.{key}" if prefix else key
      flatten_json(value, key, flattened, new_prefix)

  # List, keep the list flattening each element
  elif isinstance(json_obj, list):
    array = []
    for i, value in enumerate(json_obj):
      array.append(flatten_json(value))
    flattened[key] = array

  # Scalar, store item
  else:
    flattened[key] = json_obj

  return flattened


