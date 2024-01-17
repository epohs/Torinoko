from flask import render_template, request, url_for, redirect
from app.main import bp
from app.models.note import Note
from app.forms import NewNoteForm





@bp.route('/')
def index():

  
  form = NewNoteForm()
  

  # TEMP for displaying all notes
  notes = Note.query.all()

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
    
    return redirect(url_for('main.view_note', slug=just_added_note.slug))

  else:
  
    # Redirect to our error page
    return redirect(url_for('main.bad_note'))






@bp.route('/note/<string:slug>')
def view_note(slug):

  if not isinstance(slug, str) or len(slug) < 5:
  
    return redirect(url_for('main.no_note'))
    
  else:
  
    note = Note.query.filter_by( slug=slug ).first()
    
    if note:
    
      return render_template('view-note.html', note=note)
      
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







