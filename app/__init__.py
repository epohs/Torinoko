from flask import Flask
from config import Config
from app.ext import db

def create_app( config_class=Config ):

  app = Flask(__name__)
  app.config.from_object(config_class)

  # Initialize Flask extensions here
  db.init_app(app)

  from app.models.note import Note

  with app.app_context():

    db.create_all()
    db.session.commit()	

    test_note = Note( content='hey this is a test note' )
    db.session.add(test_note)
    db.session.commit()



  # Register blueprints here
  from app.main import bp as main_bp

  app.register_blueprint(main_bp)

  return app
