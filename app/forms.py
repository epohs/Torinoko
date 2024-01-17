# Probably should move this stuff to a separate file
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, HiddenField
from wtforms import validators





class NewNoteForm(FlaskForm):

  new_note = TextAreaField(u'New note', [validators.DataRequired(), validators.Length(max=2500)])
  submit_btn = SubmitField(u'Create note')




class ViewNoteForm(FlaskForm):

  note_slug = HiddenField("Slug")
  submit_btn = SubmitField(u'View note')
