import base64, hashlib
import numpy as np
import string
from secrets import choice
from functools import partial








# https://stackoverflow.com/questions/44432945/generating-own-key-with-python-fernet
def gen_fernet_key(passcode:bytes) -> bytes:

  passcode = passcode.encode('utf-8')

  assert isinstance(passcode, bytes)
  hlib = hashlib.md5()
  hlib.update(passcode)
  return base64.urlsafe_b64encode(hlib.hexdigest().encode('latin-1'))







# Create a number of potential random strings to be used as note slugs
def produce_slugs(amount_of_keys, min_max=None, _randint=np.random.randint):
  
  if min_max is None:
    
    min_max = { 'min':5, 'max':20 }
  
  keys = set()
  
  pickchar = partial(
    np.random.choice,
    np.array(list(string.ascii_lowercase + string.ascii_uppercase + string.digits)))
    
  while len(keys) < amount_of_keys:
    keys |= {''.join([pickchar() for _ in range( _randint(min_max['min'], min_max['max']) )]) for _ in range(amount_of_keys - len(keys))}

  return keys







# Take a list of potential slugs, check the database to make sure the
# slug is not already in use and return the first free one.
def get_good_slug(model_obj):
  
  
  # Each dictionary in this list represents one batch of slugs.
  # min/max refers to the lengths of the slugs in each batch.
  slug_ranges = [
                  { 'min':5, 'max':7 },
                  { 'min':8, 'max':12 },
                  { 'min':13, 'max':20 }
                ]
                
  # Loop through each batch.
  # We start with the shorter slugs just to have a nicer URL,
  # getting longer as we go to reduce the risk of collision.
  for i in range( len(slug_ranges) ):
  
  
    slug_range = slug_ranges[i]
    
  
    # We pull 15 slugs for each batch
    slugs = produce_slugs(15, slug_range)
  
    good_slug = None
  
  
    # Loop through our random slugs checking for the first slug
    # that doesn't already exist in the database
    for slug in slugs:
  
      found_row = model_obj.query.filter_by( slug=slug ).first()
  
      if not found_row:
  
        good_slug = slug
  
        break
    
    # If we have a good slug and a valid form
    # we're ready to create a new note.
    # Otherwise, something weird wend wrong
    if good_slug:
    
      return good_slug



  # If we reach this point we have looped through all of our batches
  # of slugs and not found an unused slug.
  return None








# Calculate an expiration timestamp based on a seconds parameter
def get_expires_at( seconds=None ):

  from datetime import datetime, timedelta

  # Default to 1 day
  default_seconds_to_add = 86400
  
  # 1 hour
  min_seconds_to_add = 3600
  
  # 7 days
  max_seconds_to_add = 604800
  


  # Determine whether the seconds fall within our min-max range
  if ( not isinstance(seconds, int) ):
  
    # This shouldn't happen because WTForms won't let a non-INT value
    # be submitted, but I'll add this for good measure.
    seconds_to_add = default_seconds_to_add
  
  elif ( int(seconds) < min_seconds_to_add ):
  
    seconds_to_add = min_seconds_to_add
    
  elif ( int(seconds) > max_seconds_to_add ):
  
    seconds_to_add = max_seconds_to_add
    
  else:
  
    # The seconds passed were within the min-max range.
    # Recast as INT just to be certain.
    seconds_to_add = int(seconds)
  
  
  # Add the number of seconds to the current timestamp and return.
  return datetime.now() + timedelta( seconds = seconds_to_add )








