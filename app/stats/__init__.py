"""
The `flask stats` command.

Usage stats for whoever runs the server. It's a command line tool
only, with no route, so none of it is reachable from the web.
"""

import os
import sys
import time

import click
from flask.cli import with_appcontext
from rich.console import Console
from rich.live import Live

from app.ext import db
from app.stats.collect import collect_stats
from app.stats.render import render_dashboard, render_json, render_oneline, render_plain








@click.command('stats')
@click.option('--days', default=30, show_default=True, type=click.IntRange(min=1),
              help='Length of the recent period, in days.')
@click.option('--json', 'as_json', is_flag=True,
              help='Print everything as JSON, for scripts.')
@click.option('--plain', is_flag=True,
              help='No color or box drawing. On automatically when output is piped or NO_COLOR is set.')
@click.option('--oneline', is_flag=True,
              help='Print a single summary line.')
@click.option('--watch', type=click.IntRange(min=1), metavar='SECONDS',
              help='Redraw every SECONDS seconds until Ctrl-C.')
@with_appcontext
def stats_command(days, as_json, plain, oneline, watch):
  """
  Show usage stats for this Torinoko database.

  Totals come from the note event log, which only records while
  TRACK_STATS is on in config.py. Times are stored in UTC and shown
  in this machine's local timezone.
  """

  if sum([ as_json, plain, oneline ]) > 1:

    raise click.UsageError('Choose only one of --json, --plain and --oneline.')

  if watch and as_json:

    raise click.UsageError('--watch can\'t be combined with --json.')


  # Fall back to plain output when there's nowhere to show color
  if not ( as_json or oneline ) and ( not sys.stdout.isatty() or os.environ.get('NO_COLOR') ):

    plain = True


  def snapshot():

    # Start a fresh session so each redraw sees current data
    db.session.remove()

    return collect_stats(days)


  if as_json:

    click.echo( render_json( snapshot() ) )

  elif oneline:

    repeat( lambda: click.echo( render_oneline( snapshot() ) ), watch )

  elif plain:

    repeat( lambda: click.echo( render_plain( snapshot() ) ), watch, clear=True )

  else:

    show_dashboard(snapshot, watch)








def repeat(draw, watch, clear=False):
  """
  Draw once, or every `watch` seconds until Ctrl-C.
  """

  try:

    while True:

      if clear and watch:

        click.clear()

      draw()

      if not watch:

        return

      time.sleep(watch)

  except KeyboardInterrupt:

    pass








def show_dashboard(snapshot, watch):
  """
  Print the Rich dashboard, or keep it live with --watch.
  """

  console = Console(highlight=False)

  if not watch:

    console.print( render_dashboard( snapshot() ) )

    return

  try:

    with Live( render_dashboard( snapshot() ), console=console, auto_refresh=False ) as live:

      while True:

        time.sleep(watch)
        live.update( render_dashboard( snapshot() ), refresh=True )

  except KeyboardInterrupt:

    pass
