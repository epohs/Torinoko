import base64
import string
from secrets import choice
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from sqlalchemy.exc import IntegrityError
from app.ext import db








def gen_fernet_key(secret:str, passphrase:str, salt:bytes) -> bytes:
  """
  Derive the key used to encrypt a note from the app's secret, the
  optional passphrase, and the note's random salt.

  Scrypt is deliberately slow and memory hungry so passphrases can't be
  cheaply brute forced, and the per-note salt means every note has to
  be attacked on its own.
  """

  key_material = f'{secret}\x00{passphrase or ""}'.encode('utf-8')

  kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)

  return base64.urlsafe_b64encode( kdf.derive(key_material) )








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








