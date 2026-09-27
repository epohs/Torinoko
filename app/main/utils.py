import base64, hashlib
import string
from secrets import choice
from sqlalchemy.exc import IntegrityError
from app.ext import db








def gen_fernet_key(passcode:bytes) -> bytes:
  """
  Accepts a string and returns a byte-like object to be used
  in the creation of a Fernet token to encrypt our notes.
  
  https://stackoverflow.com/questions/44432945/generating-own-key-with-python-fernet
  """
  
  passcode = passcode.encode('utf-8')

  assert isinstance(passcode, bytes)
  
  hlib = hashlib.md5()
  hlib.update(passcode)
  
  return base64.urlsafe_b64encode(hlib.hexdigest().encode('latin-1'))







def gen_slug(length:int) -> str:
  """
  Create a random string to be used as a note slug.
  """

  slug_chars = string.ascii_lowercase + string.ascii_uppercase + string.digits

  return ''.join( choice(slug_chars) for _ in range(length) )








def get_good_slug(note, min_length:int, max_length:int, attempts_per_length:int=3):
  """
  Save a note under the shortest random slug that isn't already in use,
  and return that slug.

  Rather than checking the database for a free slug first, we try the
  insert and let the unique constraint on slug reject a collision.
  Checking first leaves a gap where another request can take the slug
  between our check and our insert.
  """

  # We start with the shortest slugs just to have a nicer URL,
  # getting longer after a few collisions to reduce the risk of more.
  for length in range( min_length, max_length + 1 ):

    for _ in range( attempts_per_length ):

      note.slug = gen_slug(length)

      db.session.add(note)

      try:

        db.session.commit()

      except IntegrityError:

        # Slug is taken. The rollback detaches the note so we can retry.
        db.session.rollback()

        continue

      return note.slug



  # If we reach this point every length collided repeatedly.
  return None









def get_expires_at( seconds=None ):
  """
  Calculate an expiration timestamp based on a seconds parameter
  """
  
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
    # We will use what was passed as the expiration for this note.
    # Recast as INT just to be certain.
    seconds_to_add = int(seconds)
  
  
  # Add the number of seconds to the current timestamp and return.
  return datetime.now() + timedelta( seconds = seconds_to_add )








