import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
  """
  Global settings for our app.
  """

  # Don't leave these values set to True in a production environment!
  DEVELOPMENT = True
  DEBUG = True
  
  # Only send the session cookie over HTTPS.
  # This is off in development so the app works over plain HTTP locally.
  SESSION_COOKIE_SECURE = not DEVELOPMENT
  
  # This secret will be the base for note encryption.
  # It will read first from an environment variable, and then use the string
  # defined here.
  # Changing this key will make ALL existing notes unreadable.
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
  
  # Set the path to our database.
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')\
        or 'sqlite:///' + os.path.join(basedir, 'data/db.sqlite')
  
  
  # Minimum and maximum lengths of note slugs.
  # Shorter slugs are tried first, getting longer only on collision.
  SLUG_MIN_LENGTH = 5
  SLUG_MAX_LENGTH = 20
  
  
  # Keep a log of note events (created, read, expired...) for `flask stats`.
  # Events hold no slugs, content or visitor details.
  TRACK_STATS = True
  
  
  # Let form CSRF tokens last as long as the browser session, so a
  # secret page left open for a while can still be submitted.
  WTF_CSRF_TIME_LIMIT = None
  
  
  # Don't store changes to the database.
  SQLALCHEMY_TRACK_MODIFICATIONS = False
