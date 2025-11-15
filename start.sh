#!/bin/bash

echo "Running migrations..."
python manage.py migrate

echo "Clearing existing events..."
python manage.py shell -c "from events.models import Event; Event.objects.all().delete(); print('Events cleared')" 2>/dev/null || echo "No events to clear"

echo "Loading event fixtures..."
python manage.py loaddata fixtures/mokkoji_events.json --verbosity 2

echo "Starting Gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2
