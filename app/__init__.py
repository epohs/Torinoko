import os
from flask import Flask
from sqlalchemy import event
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

    # Have SQLite overwrite deleted notes on disk, rather than
    # just marking their space as free to be reused later.
    if db.engine.dialect.name == 'sqlite':

      @event.listens_for(db.engine, 'connect')
      def enable_secure_delete(dbapi_connection, connection_record):

        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA secure_delete = ON')
        cursor.close()

    # Create tables if they don't exist	
    db.create_all()
    db.session.commit()	



  
  app.register_blueprint(main_bp)


  # Version static URLs by file mtime so browser and CDN caches
  # pick up changes as soon as they are deployed.
  @app.url_defaults
  def version_static_urls(endpoint, values):

    if endpoint == 'static' and 'filename' in values:

      file_path = os.path.join(app.static_folder, values['filename'])

      if os.path.isfile(file_path):

        values['v'] = int(os.stat(file_path).st_mtime)


 

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
