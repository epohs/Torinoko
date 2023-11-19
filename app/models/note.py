from app.ext import db

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)

    def __repr__(self):
        return f'<Note "{self.title}">'