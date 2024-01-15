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
  
    from app.ext import db

    new_note = Note( content=form.new_note.data )
    db.session.add(new_note)
    db.session.commit()
    
    return redirect(url_for('main.index'))

  else:
  
    # Redirect to our error page
    return redirect(url_for('main.bad_note'))









@bp.route('/new/error')
def bad_note():

  return render_template('invalid-note.html')







