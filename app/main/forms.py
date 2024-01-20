# Probably should move this stuff to a separate file
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, HiddenField
from wtforms import validators





class NewNoteForm(FlaskForm):

  new_note = TextAreaField(u'New note', [validators.DataRequired(), validators.Length(max=2500)])
  passphrase = StringField(u'Passphrase',[validators.Length(max=128, message='Passphrase is 128 characters max')])
  
  submit_btn = SubmitField(u'Create note')




class ViewNoteForm(FlaskForm):

  note_slug = HiddenField(u'Slug')
  passphrase = StringField(u'Passphrase',[validators.Length(max=128, message='Passphrase is 128 characters max')])

  submit_btn = SubmitField(u'View note')
