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

    #test_note = Note( content='hey this is a test note' )
    #db.session.add(test_note)
    #db.session.commit()



  # Register blueprints here
  from app.main import bp as main_bp
  from app.main import routes
  
  app.register_blueprint(main_bp)

	
 

  # Disable browser caching if we're in debug mode
  if app.config['DEBUG']:

    @app.after_request
    def add_header(r):
	
      r.headers["Cache-Control"] = "no-store, must-revalidate"
      r.headers["Pragma"] = "no-cache"
      r.headers["Expires"] = "0"

      return r

  return app
