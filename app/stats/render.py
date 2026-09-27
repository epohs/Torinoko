"""
Turn a Stats snapshot into something to print.

The dashboard uses Rich. Plain, one line and JSON output are
plain strings, for pipes, scripts and terminals without color.
"""

import json
from dataclasses import asdict
from datetime import datetime

from rich.console import Group
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from app.stats.collect import Stats


# The yellow used across the site
ACCENT = '#ffbe00'

SPARK_CHARS = ' ▁▂▃▄▅▆▇█'
SPARK_WIDTH = 30
BAR_WIDTH = 16








def render_dashboard(stats:Stats) -> Group:
  """
  The full Rich dashboard.
  """

  sections = [ summary_panel(stats), Text() ]

  if not stats.tracking:

    sections += [ Text('  stats tracking is off · set TRACK_STATS = True in config.py', style='dim'), Text() ]

  sections += [
    heading(f'outcomes · last {period(stats)}'),
    indent( outcome_rows(stats) ),
    Text(),
    heading(f'habits · last {period(stats)}'),
    indent( habit_rows(stats) ),
    Text(),
    heading(f'timing · last {period(stats)}'),
    indent( timing_rows(stats) ),
    Text(),
    heading('health'),
    indent( health_rows(stats) ),
  ]

  return Group(*sections)








def summary_panel(stats:Stats) -> Panel:
  """
  The boxed headline numbers.
  """

  grid = Table.grid(padding=(0, 2))
  grid.add_column(style='dim')
  grid.add_column(justify='right', style='bold')
  grid.add_column(style=ACCENT)

  grid.add_row('created, all time', f'{stats.created_all_time:,}', '')
  grid.add_row('live right now', f'{stats.live_now:,}', '')
  grid.add_row(f'last {period(stats)}', f'{stats.created_recent:,}', sparkline(stats.daily_created))

  return Panel(grid, title=f'[bold {ACCENT}]Torinoko[/]', title_align='left', border_style='grey50', expand=False, padding=(0, 2))








def outcome_rows(stats:Stats) -> Table:
  """
  How notes ended: read, expired unread, or locked out.
  """

  table = rows_table()

  for label, count, style in (
                               ('read', stats.read, 'green'),
                               ('expired', stats.expired, 'yellow'),
                               ('locked', stats.locked, 'red'),
                             ):

    share = count / stats.finished if stats.finished else 0
    table.add_row(label, bar(share, style), percent(share if stats.finished else None), f'{count:,}')

  return table








def habit_rows(stats:Stats) -> Table:
  """
  Passphrase use and which expiry options get picked.
  """

  table = rows_table()
  table.add_row('passphrase', bar(stats.passphrase_share or 0, ACCENT), percent(stats.passphrase_share), '')

  total = sum( count for _, count in stats.expiry_choices )

  for label, count in stats.expiry_choices:

    share = count / total if total else 0
    table.add_row(f'  {label}', bar(share, 'dim'), percent(share if total else None), f'{count:,}')

  return table








def timing_rows(stats:Stats) -> Table:
  """
  How quickly notes get read, and when people make them.
  """

  table = rows_table(columns=2)
  table.add_row('median time to read', duration(stats.median_seconds_to_read))
  table.add_row('busiest day', stats.busiest_weekday or '—')
  table.add_row('busiest hour', f'{stats.busiest_hour:02d}:00' if stats.busiest_hour is not None else '—')

  return table








def health_rows(stats:Stats) -> Table:
  """
  Wrong passphrases, the next expiry, and the database size.
  """

  table = rows_table(columns=2)
  table.add_row('wrong passphrases', f'{stats.wrong_passphrases:,} in the last {period(stats)}')
  table.add_row('next expiry', until(stats.next_expiry, stats.generated_at))
  table.add_row('database size', file_size(stats.database_bytes))

  return table








def render_plain(stats:Stats) -> str:
  """
  The same numbers as the dashboard, without color or box drawing.
  """

  p = period(stats)

  lines = [
    f'Torinoko stats · last {p}',
    '',
    f'created, all time      {stats.created_all_time:,}',
    f'live right now         {stats.live_now:,}',
    f'created, last {p:<9}{stats.created_recent:,}',
    '',
    f'read                   {stats.read:,} ({percent(share(stats.read, stats.finished))})',
    f'expired unread         {stats.expired:,} ({percent(share(stats.expired, stats.finished))})',
    f'locked out             {stats.locked:,} ({percent(share(stats.locked, stats.finished))})',
    '',
    f'passphrase used        {percent(stats.passphrase_share)}',
    'expiry chosen          ' + ', '.join( f'{label} {count}' for label, count in stats.expiry_choices ),
    '',
    f'median time to read    {duration(stats.median_seconds_to_read)}',
    f'busiest day            {stats.busiest_weekday or "-"}',
    'busiest hour           ' + ( f'{stats.busiest_hour:02d}:00' if stats.busiest_hour is not None else '-' ),
    '',
    f'wrong passphrases      {stats.wrong_passphrases:,}',
    f'next expiry            {until(stats.next_expiry, stats.generated_at)}',
    f'database size          {file_size(stats.database_bytes)}',
  ]

  if not stats.tracking:

    lines += [ '', 'stats tracking is off (TRACK_STATS in config.py)' ]

  return '\n'.join(lines).replace('—', '-')








def render_oneline(stats:Stats) -> str:
  """
  A single summary line, for a login message or a quick check.
  """

  return ' · '.join([
    'torinoko',
    f'{stats.live_now:,} live',
    f'{stats.created_recent:,} in {stats.days}d',
    f'{stats.created_all_time:,} all time',
    f'{percent(stats.read_rate)} read',
  ]).replace('—', '-')








def render_json(stats:Stats) -> str:
  """
  Everything, as JSON. Times are ISO 8601 in UTC.
  """

  data = asdict(stats)
  data['read_rate'] = stats.read_rate

  return json.dumps( data, indent=2, default=lambda value: value.isoformat() if isinstance(value, datetime) else str(value) )








def rows_table(columns:int=4) -> Table:
  """
  A borderless table for one dashboard section.

  Four columns are label, bar, percent and count. Two are label and value.
  """

  table = Table.grid(padding=(0, 2))
  table.add_column(style='dim', min_width=20)

  if columns == 4:

    table.add_column()
    table.add_column(justify='right')
    table.add_column(justify='right')

  else:

    table.add_column()

  return table








def indent(renderable) -> Padding:

  return Padding(renderable, (0, 0, 0, 2), expand=False)



def heading(label:str) -> Text:

  return Text(f'  {label}', style=f'bold {ACCENT}')



def period(stats:Stats) -> str:

  return f'{stats.days} day' if stats.days == 1 else f'{stats.days} days'



def share(part:int, whole:int) -> float | None:

  return part / whole if whole else None



def percent(value:float | None) -> str:

  return '—' if value is None else f'{value:.0%}'



def bar(value:float, style:str) -> Text:
  """
  A filled bar for a share between 0 and 1.
  """

  filled = round( max(0.0, min(1.0, value)) * BAR_WIDTH )

  return Text.assemble( ('█' * filled, style), ('░' * (BAR_WIDTH - filled), 'dim') )



def sparkline(values:list[int]) -> str:
  """
  A small bar chart of daily counts, squeezed to SPARK_WIDTH characters.
  """

  if not values:

    return ''

  # Long periods are grouped so the line stays short
  size = -(-len(values) // SPARK_WIDTH)
  buckets = [ sum( values[i:i + size] ) for i in range(0, len(values), size) ]
  peak = max(buckets)

  if not peak:

    return SPARK_CHARS[1] * len(buckets)

  return ''.join( SPARK_CHARS[ max(1, round( count / peak * (len(SPARK_CHARS) - 1) )) if count else 1 ] for count in buckets )



def duration(seconds:float | None) -> str:
  """
  A short human duration, like 2h 14m.
  """

  if seconds is None:

    return '—'

  minutes = int(seconds // 60)

  if minutes < 1:

    return 'under a minute'

  days, minutes = divmod(minutes, 1440)
  hours, minutes = divmod(minutes, 60)

  parts = [ f'{days}d' if days else '', f'{hours}h' if hours else '', f'{minutes}m' if minutes and not days else '' ]

  return ' '.join( part for part in parts if part )



def until(moment:datetime | None, now:datetime) -> str:

  return '—' if moment is None else f'in {duration( (moment - now).total_seconds() )}'



def file_size(size:int | None) -> str:

  if size is None:

    return '—'

  for unit in ('bytes', 'KB', 'MB', 'GB'):

    if size < 1024 or unit == 'GB':

      return f'{size:,} {unit}' if unit == 'bytes' else f'{size:,.1f} {unit}'

    size /= 1024
