#!/bin/bash
set -e

echo "=== Waiting for PostgreSQL ==="
python wait_for_db.py

echo "=== Running migrations ==="
python manage.py makemigrations lotto
python manage.py migrate

echo "=== Creating superuser ==="
python create_superuser.py

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Starting Gunicorn ==="
exec gunicorn lottoproject.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --access-logfile - \
    --error-logfile -
