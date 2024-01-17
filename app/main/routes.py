from flask import render_template, request, url_for, redirect
from app.ext import db
from app.main import bp
from app.models.note import Note
from app.forms import NewNoteForm, ViewNoteForm





@bp.route('/')
def index():

  
  form = NewNoteForm()
  

  # TEMP for displaying all notes
  notes = Note.query.all()


  # Look into the package `Wonderwords` for generating a random passphrase
  # https://pypi.org/project/wonderwords/


  return render_template('index.html', form=form, notes=notes)






@bp.route('/new', methods=['GET', 'POST'])
def new_note():

  form = NewNoteForm(request.form)

  if request.method == 'POST' and form.validate():
  
    from app.ext import db

    new_note = Note( content=form.new_note.data )
    db.session.add(new_note)
    db.session.commit()
    
    just_added_note = Note.query.get(new_note.id)
    
    return redirect(url_for('main.secret', slug=just_added_note.slug))

  else:
  
    # Redirect to our error page
    return redirect(url_for('main.bad_note'))






@bp.route('/secret/<string:slug>')
def secret(slug):


  if not isinstance(slug, str) or len(slug) < 5:
  
    return redirect(url_for('main.no_note'))
    
  else:
  
    note = Note.query.filter_by( slug=slug ).first()
    
    if note:
    
      form = ViewNoteForm(request.form, note_slug=slug)
    
      return render_template('secret.html', slug=slug, form=form)
      
    else:
    
      return redirect(url_for('main.no_note'))





@bp.route('/note/<string:slug>', methods=['POST'])
def view_note(slug):

  if not isinstance(slug, str) or len(slug) < 5:
  
    return redirect(url_for('main.no_note'))
    
  else:
  
    note = Note.query.filter_by( slug=slug ).first()
    
    if note:
    
      # Render the template, then delete the note.
      try:
      
        return render_template('view-note.html', note=note)
      
      finally:
      
        db.session.delete(note)
        db.session.commit()
      
    else:
    
      return redirect(url_for('main.no_note'))









# @todo these two routes should be combined
# to use unique URLs, but the same template
# with the content being passed as a parameter
# and descriptive of why the user got an error.
@bp.route('/no-note')
def no_note():

  return render_template('no-note.html')

@bp.route('/new/error')
def bad_note():

  return render_template('invalid-note.html')







@bp.app_errorhandler(405)
def method_not_allowed(e):

  url_segments = request.path.split('/')
  resource_id = url_segments[2]

  if (
        ( isinstance(resource_id, str) ) and 
        ( 5 <= len(resource_id) <= 20) and
        ( request.path == url_for('main.view_note', slug=resource_id) )
     ):

    return redirect( url_for('main.secret', slug=resource_id) )

  else:

    return redirect( url_for('main.index') )




