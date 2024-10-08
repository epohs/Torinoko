from flask import Flask
from config import Config
from app.ext import db





def create_app( config_class=Config ):

  """
  This is the core of the entire app.
  All initialization begins here.
  """

  app = Flask(__name__)
  app.config.from_object(config_class)


  # Register blueprints and routes
  from app.main import bp as main_bp
  from app.main import routes


  with app.app_context():

    # Initialize the database
    db.init_app(app)

    # Create tables if they don't exist	
    db.create_all()
    db.session.commit()	



  
  app.register_blueprint(main_bp)

	
 

  # Disable browser caching if we're in debug mode
  if app.config['DEBUG']:

    @app.after_request
    def add_header(r):
	
      r.headers["Cache-Control"] = "no-store, must-revalidate"
      r.headers["Pragma"] = "no-cache"
      r.headers["Expires"] = "0"

      return r



  # Return the app object to be used globally
  return app
