"""
Gather usage stats from the database.

Everything here only reads. Times are stored in UTC and converted to
the local timezone only where it matters: grouping by day and hour.
"""

import calendar
import os
import statistics
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta

from flask import current_app
from sqlalchemy import func, select

from app.ext import db
from app.main.forms import NewNoteForm
from app.main.routes import MAX_BAD_VIEWS
from app.main.utils import utc_now
from app.models.note import Note
from app.models.note_event import NoteEvent








@dataclass(frozen=True, slots=True)
class Stats:
  """
  A snapshot of usage for the last `days` days, plus all-time totals.
  """

  days: int
  generated_at: datetime
  tracking: bool

  created_all_time: int
  created_recent: int
  live_now: int
  daily_created: list[int]

  read: int
  expired: int
  locked: int

  passphrase_share: float | None
  expiry_choices: list[tuple[str, int]]

  median_seconds_to_read: float | None
  busiest_weekday: str | None
  busiest_hour: int | None

  wrong_passphrases: int
  next_expiry: datetime | None
  database_bytes: int | None


  @property
  def finished(self) -> int:
    """
    Notes that reached an end in the period, one way or another.
    """

    return self.read + self.expired + self.locked


  @property
  def read_rate(self) -> float | None:
    """
    Share of finished notes that were actually read.
    """

    return self.read / self.finished if self.finished else None








def collect_stats(days:int) -> Stats:
  """
  Build a Stats snapshot for the last `days` days.
  """

  now = utc_now()
  since = now - timedelta(days=days)


  # Event counts, all time and for the recent period
  all_time = event_counts()
  recent = event_counts(since)


  # Created events carry the details for habits and timing
  created = db.session.execute(
              select( NoteEvent.occurred_at, NoteEvent.has_passphrase, NoteEvent.expires_in )
              .where( NoteEvent.event == 'created', NoteEvent.occurred_at >= since )
            ).all()

  read_times = db.session.scalars(
                 select( NoteEvent.seconds_to_read )
                 .where( NoteEvent.event == 'read', NoteEvent.occurred_at >= since )
               ).all()


  # Notes that could still be read right now
  live_now, next_expiry = db.session.execute(
                            select( func.count(Note.id), func.min(Note.expires_at) )
                            .where( Note.expires_at > now, Note.bad_view_count < MAX_BAD_VIEWS )
                          ).one()


  # Group creation times by local day, weekday and hour
  local_times = [ row.occurred_at.astimezone() for row in created ]

  weekdays = Counter( t.weekday() for t in local_times )
  hours = Counter( t.hour for t in local_times )

  passphrase_flags = [ row.has_passphrase for row in created if row.has_passphrase is not None ]
  read_seconds = [ s for s in read_times if s is not None ]


  return Stats(
    days=days,
    generated_at=now,
    tracking=current_app.config.get('TRACK_STATS', False),
    created_all_time=all_time['created'],
    created_recent=recent['created'],
    live_now=live_now,
    daily_created=daily_counts(local_times, now, days),
    read=recent['read'],
    expired=recent['expired'],
    locked=recent['locked'],
    passphrase_share=( sum(passphrase_flags) / len(passphrase_flags) ) if passphrase_flags else None,
    expiry_choices=expiry_choice_counts( row.expires_in for row in created ),
    median_seconds_to_read=statistics.median(read_seconds) if read_seconds else None,
    busiest_weekday=calendar.day_name[ weekdays.most_common(1)[0][0] ] if weekdays else None,
    busiest_hour=hours.most_common(1)[0][0] if hours else None,
    wrong_passphrases=recent['wrong_passphrase'],
    next_expiry=next_expiry,
    database_bytes=database_size(),
  )








def event_counts(since:datetime | None=None) -> Counter:
  """
  Count events by type, optionally only those since a point in time.
  """

  query = select( NoteEvent.event, func.count() ).group_by( NoteEvent.event )

  if since is not None:

    query = query.where( NoteEvent.occurred_at >= since )

  return Counter( dict( db.session.execute(query).all() ) )








def daily_counts(local_times:list[datetime], now:datetime, days:int) -> list[int]:
  """
  Count creations per local calendar day, oldest first, ending today.
  """

  today = now.astimezone().date()
  per_day = Counter( t.date() for t in local_times )

  return [ per_day[ today - timedelta(days=offset) ] for offset in reversed( range(days) ) ]








def expiry_choice_counts(expires_in_values) -> list[tuple[str, int]]:
  """
  Count which expiry option each note used, labelled like the form.

  Values that don't match an option exactly are counted
  under the nearest one.
  """

  choices = [ ( int(seconds), label ) for seconds, label in NewNoteForm.expires_choices ]
  counts = Counter()

  for expires_in in expires_in_values:

    if expires_in is None:

      continue

    nearest = min( choices, key=lambda choice: abs(choice[0] - expires_in) )
    counts[ nearest[1] ] += 1

  return [ ( label, counts[label] ) for _, label in choices ]








def database_size() -> int | None:
  """
  Size of the SQLite database file in bytes, or None for other databases.
  """

  url = db.engine.url

  if url.get_backend_name() != 'sqlite' or not url.database:

    return None

  try:

    return os.path.getsize(url.database)

  except OSError:

    return None
