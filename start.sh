#!/bin/bash

echo "Running migrations..."
python manage.py migrate

echo "Loading event fixtures..."
python manage.py loaddata fixtures/mokkoji_events.json --verbosity 0 || echo "Fixtures already loaded or error occurred"

echo "Starting Gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2
