# Torinoko

## Lightweight encrypted note sharing tool

Create an ecrypted note with a unique URL to share with someone else. 

Each note has an expiration date, and an optional passphrase. All notes are enrypted in the database. If you use a passphrase it will not be possible to read the note without knowing that passphrase, even with direct access to the database.

This project takes most of it's inspiration from [Onetimesecret](https://onetimesecret.com).


## Basic Requirements

* [uv](https://docs.astral.sh/uv/)
* [Python 3.11+](https://www.python.org) (uv will install it if needed)
* [Sqlite 3](https://sqlite.org)


## Quick install

* Clone this repository.
* `cd` into it.
* Install dependencies `uv sync`.
* Create config.py. Use config-sample.py as a guide.
* Run the project in debug mode with `uv run flask --debug run`.


## Detailed installation example

Todo: Add a more detailed walkthrough of setting up Nginx and Gunicorn on a raspberry pi.

## Deployment notes

* Set `DEVELOPMENT` and `DEBUG` to `False` in config.py.
* Run gunicorn with `--preload` so the database is set up once, before the workers start. For example `uv run gunicorn --preload -w 2 -b 127.0.0.1:8000 wsgi:app`.
* Rate limiting is left to the web server. Short slugs are only as safe as they are slow to guess, so limit requests to `/secret/` and `/note/`. With Nginx, `limit_req` works well.
* If the web server sends a Content Security Policy, the app's JavaScript works without `'unsafe-inline'`.
