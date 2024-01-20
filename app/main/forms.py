from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, HiddenField
from wtforms import validators





class NewNoteForm(FlaskForm):

  new_note = TextAreaField(u'New note', [validators.DataRequired(), validators.Length(max=2500)])
  passphrase = StringField(u'Passphrase',[validators.Length(max=128, message='Passphrase is 128 characters max')])
  
  expires_choices=[
            ('3600',   '1 hour'),
            ('10800',  '3 hours'),
            ('43200',  '12 hours'),
            ('86400',  '1 day'),
            ('259200', '3 days'),
            ('604800',  '7 days')
          ]

  expires = SelectField(u'Expires in', choices=expires_choices, default = '86400', coerce=int)


  submit_btn = SubmitField(u'Create note')




class ViewNoteForm(FlaskForm):

  note_slug = HiddenField(u'Slug')
  passphrase = StringField(u'Passphrase',[validators.Length(max=128, message='Passphrase is 128 characters max')])

  submit_btn = SubmitField(u'View note')
