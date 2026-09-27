from flask import current_app
from app.ext import db
from app.main.utils import utc_now
from app.models.note import UTCDateTime





class NoteEvent(db.Model):
  """
  A record of something that happened to a note, kept for usage stats.

  Events never hold a slug, note content, or anything about the visitor,
  so they can't be tied back to a note or a person.
  """

  __tablename__ = "note_events"

  id = db.Column(db.Integer, primary_key=True)

  # created, read, wrong_passphrase, locked, or expired
  event = db.Column(db.Text, nullable=False)
  occurred_at = db.Column(UTCDateTime, nullable=False, default=utc_now, index=True)

  # Only set on created events
  has_passphrase = db.Column(db.Boolean, nullable=True)
  expires_in = db.Column(db.Integer, nullable=True)

  # Only set on read events
  seconds_to_read = db.Column(db.Integer, nullable=True)



  @classmethod
  def record(cls, event, **fields):
    """
    Add an event to the current session, if stats tracking is on.

    The caller commits, so the event is saved together with the
    change it describes.
    """

    if not current_app.config.get('TRACK_STATS', False):

      return

    db.session.add( cls(event=event, **fields) )
