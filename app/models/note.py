from config import Config
from app.ext import db, gen_fernet_key
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property


from cryptography.fernet import Fernet





class Note(db.Model):

  __tablename__ = "notes"


  key = gen_fernet_key( Config.SECRET_KEY.encode('utf-8') )
  fernet = Fernet(key)
  

  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.Text, nullable=True, unique=False)
  slug = db.Column(db.Text, nullable=False, unique=True)
  created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)



  def __repr__(self):

    return f'<Note "{self.id}">'



  def __init__(self, content, slug):
  
    self.content = self.fernet.encrypt( bytes(content.encode('utf-8')) )
    self.slug = slug

    
  @hybrid_property    
  def clean_note(self):
    
    return self.fernet.decrypt( self.content ).decode('utf-8')



