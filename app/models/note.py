from config import Config
from app.ext import db
from app.main.utils import gen_fernet_key, get_good_slug, get_expires_at
from datetime import datetime, timezone
from sqlalchemy.ext.hybrid import hybrid_property


from cryptography.fernet import Fernet





class Note(db.Model):

  __tablename__ = "notes"
  
  secret = Config.SECRET_KEY
  

  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.Text, nullable=True, unique=False)
  slug = db.Column(db.Text, nullable=False, unique=True)
  created_at = db.Column(db.DateTime(timezone=True), default=datetime.now)
  expires_at = db.Column(db.DateTime(timezone=True), default=datetime.now)



  def __repr__(self):

    return f'<Note "{self.slug}">'



  def __init__(self, content, passphrase=None, expires=None):
  
    

    #print( 'passphrase: ', passphrase )
    
    if passphrase:
    
      #print( 'passphrase (',passphrase,') mixed with secret (', self.secret, ')' )
    
      key_seed = self.secret.join( passphrase )
      
    else:
    
      #print( 'no passphrase found' )
    
      key_seed = self.secret
  
  
    key = gen_fernet_key( key_seed )
    fernet = Fernet(key)
  
    self.content = fernet.encrypt( bytes(content.encode('utf-8')) )
    self.slug = get_good_slug(self)
    
    self.expires_at = get_expires_at(expires)



