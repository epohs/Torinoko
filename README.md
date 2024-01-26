# Torinoko

## Lightweight encrypted note sharing tool

Create an ecrypted note with a unique URL to share with someone else. 

Each note has an expiration date, and an optional passphrase. All notes are enrypted in the database. If you use a passphrase it will not be possible to read the note without knowing that passphrase, even with direct access to the database.

This project takes most of it's inspiration from [Onetimesecret](https://onetimesecret.com).


## Basic Requirements

* [Python 3.8](https://www.python.org)
* [Sqlite 3](https://sqlite.org)


## Quick install

* Clone this repository.
* `cd` into it.
* Create Virtual environment `python -m venv .venv`.
* Switch to the virtual environment `source .venv/bin/activate`.
* Install requirements `pip install -r requirements.txt`.
* Create config.py. Use config-sample.py as a guide.
* Run the project in debug mode with `flask --debug run`.


## Detailed installation example

Todo: Add a more detailed walkthrough of setting up Nginx and Gunicorn on a raspberry pi

## To-do

 * Make min and max slug lengths config variables.
 * Add rate limitting.
 * Switch encryption method to AES_GCM.