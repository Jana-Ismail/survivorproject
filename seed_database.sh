#!/bin/bash

rm db.sqlite3
rm -rf ./survivorapi/migrations
python3 manage.py migrate
python3 manage.py makemigrations survivorapi
python3 manage.py migrate survivorapi
python3 manage.py loaddata users
python3 manage.py loaddata tokens
python3 manage.py loaddata seasons
python3 manage.py loaddata survivors
python3 manage.py loaddata tribes
python3 manage.py loaddata survivor_tribes
python3 manage.py loaddata season_logs
python3 manage.py loaddata survivor_logs