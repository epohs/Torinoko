from config import Config
from app.ext import db
from cryptography.fernet import Fernet
from sqlalchemy_utils import EncryptedType

class Note(db.Model):

  key = Config.SECRET_KEY

  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(EncryptedType(db.Text, key), nullable=True, unique=False)

  def __repr__(self):

    return f'<Note "{self.title}">'
