from flask import render_template, request, url_for, redirect
from app.main import bp
from app.models.note import Note


# Probably should move this stuff to a separate file
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms import validators


class NewNoteForm(FlaskForm):

  new_note = TextAreaField(u'New note', [validators.DataRequired(), validators.Length(max=2500)])
  submit_btn = SubmitField(u'Create note')




@bp.route('/')
def index():

  
  form = NewNoteForm()
  

  # TEMP for displaying all notes
  notes = Note.query.all()

  return render_template('index.html', form=form, notes=notes)






@bp.route('/new', methods=['GET', 'POST'])
def new():

  form = NewNoteForm(request.form)

  if request.method == 'POST' and form.validate():
  
    from app.ext import produce_slugs

    # Get a group of potential random slugs
    slugs = produce_slugs(15)
  
    good_slug = None

  
    # Loop through our random slugs checking for the first slug
    # that doesn't already exist in the database
    for slug in slugs:

      found_row = Note.query.filter_by( slug=slug ).first()

      if not found_row:

        good_slug = slug

        break
    
    # If we have a good slug and a valid form
    # we're ready to create a new note.
    # Otherwise, something weird wend wrong
    if good_slug:
    
      from app.ext import db
    
      new_note = Note( content=form.new_note.data, slug=good_slug )
      db.session.add(new_note)
      db.session.commit()
      
      return redirect(url_for('main.index'))
      
    else:
    
      # Should probably create a new error page for situations like this
      return redirect(url_for('main.bad_note'))

  else:
  
    # Redirect to our error page
    return redirect(url_for('main.bad_note'))
    
    
  
  return render_template('new.html', slugs=slugs, good_slug=good_slug)








@bp.route('/new/error')
def bad_note():

  return render_template('invalid-note.html')







