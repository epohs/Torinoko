from flask_sqlalchemy import SQLAlchemy
import base64, hashlib


db = SQLAlchemy()





# https://stackoverflow.com/questions/44432945/generating-own-key-with-python-fernet
def gen_fernet_key(passcode:bytes) -> bytes:
  assert isinstance(passcode, bytes)
  hlib = hashlib.md5()
  hlib.update(passcode)
  return base64.urlsafe_b64encode(hlib.hexdigest().encode('latin-1'))
  
  
  

import string
from secrets import choice
import numpy as np
from functools import partial

def produce_slugs(amount_of_keys, _randint=np.random.randint):
  
  keys = set()
  
  pickchar = partial(
    np.random.choice,
    np.array(list(string.ascii_lowercase + string.ascii_uppercase + string.digits)))
    
  while len(keys) < amount_of_keys:
    keys |= {''.join([pickchar() for _ in range(_randint(5, 20))]) for _ in range(amount_of_keys - len(keys))}

  return keys
  
  
  