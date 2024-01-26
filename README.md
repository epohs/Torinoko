# Torinoko

## Lightweight encrypted note sharing tool


[Quick Install](#-quick-install)
[To-do](#-to-do)

Create an ecrypted note with a unique URL to share with someone else. Each note has an expiration date, and an optional passphrase. All notes are enrypted in the database. If you use a passphrase the note will not be able to be read without knowing that passphrase, even with direct access to the database.

This project takes most of it's inspiration from [Onetimesecret](https://onetimesecret.com).


## Quick install

* Clone this repository.
* `cd` into it.
* Create Virtual environment `python -m venv .venv`.
* Switch to the virtual environment `source .venv/bin/activate`.
* Install requirements `pip install -r requirements.txt`.
* Create config.py. Use config-sample.py as a guide.


## To-do

 * Make min and max slug lengths config variables.
 * Switch encryption method to AES_GCM.