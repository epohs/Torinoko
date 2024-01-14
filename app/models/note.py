from config import Config
from app.ext import db
from datetime import datetime
from cryptography.fernet import Fernet
#from sqlalchemy_utils import EncryptedType
from sqlalchemy.ext.hybrid import hybrid_property

import base64, hashlib

# https://stackoverflow.com/questions/44432945/generating-own-key-with-python-fernet
def gen_fernet_key(passcode:bytes) -> bytes:
    assert isinstance(passcode, bytes)
    hlib = hashlib.md5()
    hlib.update(passcode)
    return base64.urlsafe_b64encode(hlib.hexdigest().encode('latin-1'))
    
    
    

class Note(db.Model):

  __tablename__ = "notes"


  key = gen_fernet_key( Config.SECRET_KEY.encode('utf-8') )
  fernet = Fernet(key)

  id = db.Column(db.Integer, primary_key=True)
 # content = db.Column(EncryptedType(db.Text, fernet), nullable=True, unique=False)
  content = db.Column(db.Text, nullable=True, unique=False)
  created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)


  def __repr__(self):

    return f'<Note "{self.id}">'


  def __init__(self, content):
  
    cipher_suite = Fernet(self.key)
  
    self.content = cipher_suite.encrypt( bytes(content.encode('utf-8')) )
    
    
    
  @hybrid_property    
  def clean_note(self):
    
    cipher_suite = Fernet(self.key)
    
    return cipher_suite.decrypt( self.content ).decode('utf-8')
