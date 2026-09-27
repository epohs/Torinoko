import os
from flask import current_app
from app.ext import db
from app.main.utils import gen_fernet_key, get_expires_at, utc_now
from datetime import timezone
from sqlalchemy.types import TypeDecorator, DateTime
from cryptography.fernet import Fernet





class UTCDateTime(TypeDecorator):
  """
  A datetime column that is always stored as UTC and always
  comes back out as a timezone aware UTC datetime.
  
  SQLite has no timezone support, so without this aware and naive
  datetimes would be silently mixed.
  """

  impl = DateTime
  cache_ok = True


  def process_bind_param(self, value, dialect):

    if value is not None:

      # Refuse naive datetimes rather than guess what timezone they are in.
      if value.tzinfo is None:

        raise ValueError('UTCDateTime requires a timezone aware datetime')

      value = value.astimezone(timezone.utc).replace(tzinfo=None)

    return value


  def process_result_value(self, value, dialect):

    if value is not None:

      value = value.replace(tzinfo=timezone.utc)

    return value








class Note(db.Model):
  """
  Define the database structure, and formatting rules for our notes.
  """

  __tablename__ = "notes"
  

  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.Text, nullable=True, unique=False)
  slug = db.Column(db.Text, nullable=False, unique=True)
  salt = db.Column(db.LargeBinary, nullable=False)
  bad_view_count = db.Column(db.Integer, default=0)
  created_at = db.Column(UTCDateTime, default=utc_now)
  expires_at = db.Column(UTCDateTime, default=utc_now)


  
  def __repr__(self):
    """
    Notes are identified by their slug.
    """

    return f'<Note "{self.slug}">'


  
  def __init__(self, content, passphrase=None, expires=None):
    """
    Set some rules and default values for how our notes must formatted.
    """
  
    # Each note gets its own random salt for key derivation.
    self.salt = os.urandom(16)
  
    # Get the encryption token.
    # If we have a passphrase it is included in the key.
    key = gen_fernet_key( current_app.config['SECRET_KEY'], passphrase, self.salt )
    fernet = Fernet(key)
  
  
    self.content = fernet.encrypt( bytes(content.encode('utf-8')) )
    
    self.expires_at = get_expires_at(expires)



