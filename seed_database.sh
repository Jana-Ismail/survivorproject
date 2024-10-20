#!/bin/bash

rm db.sqlite3
rm -rf ./survivorapi/migrations
python3 manage.py migrate
python3 manage.py makemigrations survivorapi
python3 manage.py migrate survivorapi
python3 manage.py loaddata users
python3 manage.py loaddata tokens

