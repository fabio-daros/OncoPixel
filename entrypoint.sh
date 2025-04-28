#!/bin/bash
# Wait for the database to rise (optionally use Sleep or Wait-For-It.sh)

echo "Migrating database..."
python manage.py migrate --noinput

echo "Starting Gunicorn..."
gunicorn oncopixel.wsgi:application --bind 0.0.0.0:8001
