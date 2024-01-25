from config import Config
from app.ext import db
from app.main.utils import gen_fernet_key, get_good_slug, get_expires_at
from datetime import datetime, timezone
from sqlalchemy.ext.hybrid import hybrid_property

# @todo Switch to AES_GCM
# @see https://asecuritysite.com/encryption/aes_gcm
from cryptography.fernet import Fernet





class Note(db.Model):
  """
  Define the database structure, and formatting rules for our notes.
  """

  __tablename__ = "notes"
  
  secret = Config.SECRET_KEY
  

  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.Text, nullable=True, unique=False)
  slug = db.Column(db.Text, nullable=False, unique=True)
  bad_view_count = db.Column(db.Integer, default=0)
  created_at = db.Column(db.DateTime(timezone=True), default=datetime.now)
  expires_at = db.Column(db.DateTime(timezone=True), default=datetime.now)


  
  def __repr__(self):
    """
    Notes are identified by their slug.
    """

    return f'<Note "{self.slug}">'


  
  def __init__(self, content, passphrase=None, expires=None):
    """
    Set some rules and default values for how our notes must formatted.
    """
  
    
    # If we have a passphrase, include it when encrypting the note.
    if passphrase:
    
      key_seed = self.secret.join( passphrase )
      
    else:
    
      key_seed = self.secret
  
  
    # Get the encryption token
    key = gen_fernet_key( key_seed )
    fernet = Fernet(key)
  
  
    self.content = fernet.encrypt( bytes(content.encode('utf-8')) )
    self.slug = get_good_slug(self)
    
    self.expires_at = get_expires_at(expires)



