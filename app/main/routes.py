import time
from flask import render_template, request, url_for, redirect, current_app, make_response
from sqlalchemy import or_, delete, update
from app.ext import db
from app.main import bp
from app.main.forms import NewNoteForm, ViewNoteForm
from app.main.utils import get_good_slug, utc_now
from app.models.note import Note
from app.models.note_event import NoteEvent







# Number of bad passphrase attempts before a note is destroyed.
MAX_BAD_VIEWS = 5








def slug_looks_valid(slug):
  """
  Check that a slug is within the configured length bounds
  before bothering the database with it.
  """

  return (
           isinstance(slug, str) and
           current_app.config['SLUG_MIN_LENGTH'] <= len(slug) <= current_app.config['SLUG_MAX_LENGTH']
         )








def get_live_note(slug):
  """
  Find a note by its slug, skipping any that have expired or been
  locked out but haven't been purged yet.
  """

  return Note.query.filter(
                            Note.slug == slug,
                            Note.expires_at > utc_now(),
                            Note.bad_view_count < MAX_BAD_VIEWS
                          ).first()








@bp.route('/')
def index():
  """
  This route doubles as the homepage and the
  create a new note page.
  """

  form = NewNoteForm()


  # Look into the package `Wonderwords` for generating a random passphrase
  # https://pypi.org/project/wonderwords/


  return render_template('index.html', form=form)








@bp.route('/new', methods=['GET', 'POST'])
def new_note():
  """
  Non-public route, used only as a receiver for new note POST data.
  
  If the data posted to this route is valid it will handle creating
  the note and redirecting to the view note route.
  """

  form = NewNoteForm()


  if request.method == 'POST' and form.validate():


    new_note = Note(
                     content=form.new_note.data,
                     passphrase=form.passphrase.data,
                     expires=form.expires.data
                   )

    slug = get_good_slug(
                          new_note,
                          current_app.config['SLUG_MIN_LENGTH'],
                          current_app.config['SLUG_MAX_LENGTH']
                        )
    
    if slug:
    
      # A new note was created. Go to the secret/share page.
      return redirect(url_for('main.secret', slug=slug))
      
    else:
      
      # Creating the new note failed.
      # The most likely cause of this happening would be
      # a conflict with all of the slugs we tried to use.
      return redirect(url_for('main.bad_note'))

  else:
  
    # Redirect to our error page
    return redirect(url_for('main.bad_note'))








@bp.route('/secret/<string:slug>')
def secret(slug):
  """
  This is the URL that will be shared to the note recipient.
  
  It is  where you will land after creating a new note.
  
  This page contains the form for entering the passphrase and viewing
  the note, and the share URL field for sharing the note.
  """


  if not slug_looks_valid(slug):
  
    return redirect(url_for('main.no_note'))
    
  else:
  
    note = get_live_note(slug)
    
    if note:
    
      form = ViewNoteForm(request.form, note_slug=slug)
      
      errors = { 'remaining_attempts' : None }
      
      if note.bad_view_count:
        
        num_remaining = MAX_BAD_VIEWS - int(note.bad_view_count)
        
        num_remaining_msg = f'{num_remaining} remaining attempt{"" if num_remaining == 1 else "s"}'
      
        errors['remaining_attempts'] = num_remaining_msg
    
      return render_template('secret.html', slug=slug, form=form, errors=errors)
      
    else:
    
      return redirect(url_for('main.no_note'))








@bp.route('/note/<string:slug>', methods=['POST'])
def view_note(slug):
  """
  Route for viewing a decrypted note.
  """


  if not slug_looks_valid(slug):
  
    return redirect(url_for('main.no_note'))


  form = ViewNoteForm()

  # Check the CSRF token and passphrase length before spending an attempt.
  if not form.validate():

    return redirect( url_for('main.secret', slug=slug) )

  else:
  
    # Query the database to see if we have a note with this slug
    note = get_live_note(slug)
    
    if note:
    
      from cryptography.fernet import Fernet, InvalidToken
      from app.main.utils import gen_fernet_key
    
      passphrase = form.passphrase.data
      
      # Hold on to these now. The commit below expires the loaded note,
      # and another request may delete its row out from under us.
      note_id = note.id
      note_content = note.content
      note_salt = note.salt
      
      
      # Claim one attempt before trying to decrypt.
      # Doing this in a single conditional UPDATE means parallel requests
      # can't squeeze in more guesses than MAX_BAD_VIEWS allows.
      # A successful view deletes the note, so the claimed attempt
      # only counts against bad passphrases.
      attempt_claimed = db.session.execute(
                          update(Note)
                          .where( Note.id == note_id, Note.bad_view_count < MAX_BAD_VIEWS )
                          .values( bad_view_count = Note.bad_view_count + 1 )
                        ).rowcount
      db.session.commit()
      
      if not attempt_claimed:
      
        return redirect( url_for('main.no_note') )
      
      
      # The passphrase, if any, is used together with the app's secret
      # and the note's salt to decrypt our note.
      key = gen_fernet_key( current_app.config['SECRET_KEY'], passphrase, note_salt )



      # Try to decrypt our note.
      # If the passphrase is incorrect the claimed attempt stands,
      # and we redirect back to the secret page.
      try:
        
        fernet = Fernet(key)
        decrypted_note = fernet.decrypt( note_content ).decode('utf-8')
    
      except (InvalidToken, TypeError):

        # If that was the last allowed attempt, destroy the note.
        # This is done here rather than in the purge so that a purge can't
        # delete a note while a correct passphrase is still being checked.
        db.session.execute(
          delete(Note).where( Note.id == note_id, Note.bad_view_count >= MAX_BAD_VIEWS )
        )
        db.session.commit()

        return redirect( url_for('main.secret', slug=slug) )
      
    
    
      # Delete the note before showing it, and only show it if this
      # request is the one that deleted it. Two requests racing each other
      # can both decrypt the note, but only one of them gets to see it.
      note_deleted = db.session.execute(
                       delete(Note).where( Note.id == note_id )
                     ).rowcount
      db.session.commit()
      
      if not note_deleted:
      
        return redirect( url_for('main.no_note') )
      
      
      response = make_response( render_template('view-note.html', note=note, decrypted_note=decrypted_note) )
      
      # Never let the decrypted note be cached anywhere.
      response.headers['Cache-Control'] = 'no-store'
      
      return response
      
    else:
    
      return redirect( url_for('main.no_note') )








# @internal these two routes could be combined
# to use unique URLs, but the same template
# with the content being passed as a parameter
# and descriptive of why the user got an error.
@bp.route('/no-note')
def no_note():
  """
  Error page used mainly when a note's slug has expired.
  """

  return render_template('no-note.html')



@bp.route('/new/error')
def bad_note():
  """
  Error page that a visitor will land on if the data from
  the new note form was invalid.
  
  This should be rare, given that WTForms will force form validation
  before submission.
  """
  
  return render_template('invalid-note.html')









# Seconds between purges of expired notes.
# Lookups skip expired notes on their own, so this only needs
# to run often enough to keep old ciphertext from piling up.
PURGE_INTERVAL = 60

last_purge = 0.0


@bp.before_request
def purge_old_notes():
  """
  Before a page request, purge all expired notes if we haven't
  done so in the last PURGE_INTERVAL seconds.
  """

  global last_purge

  now = time.monotonic()

  if now - last_purge < PURGE_INTERVAL:

    return

  last_purge = now


  current_timestamp = utc_now()

  # Query to delete rows with expired timestamps
  expired_notes = delete(Note).where(
                                      or_(
                                           Note.expires_at < current_timestamp,  # Expired notes
                                           Note.expires_at.is_(None)             # Notes with null expires_at
                                         )
                                    )


  # Execute the query
  db.session.execute(expired_notes)
  db.session.commit()










@bp.route('/note/<string:slug>', methods=['GET'])
def view_note_get(slug):
  """
  A direct hit to the view note URL, usually from a refresh
  or a shared link. The view_note route only accepts POST, so
  send it to the secret page and let that route handle the lookup.
  """

  return redirect( url_for('main.secret', slug=slug) )








@bp.app_errorhandler(405)
def method_not_allowed(e):
  """
  Handle 'method not allowed' errors by just going home.
  """

  return redirect( url_for('main.index') )
