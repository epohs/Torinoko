from flask import render_template
from app.main import bp
from app.models.note import Note




@bp.route('/')
def index():

  notes = Note.query.all()

  return render_template('index.html', notes=notes)


