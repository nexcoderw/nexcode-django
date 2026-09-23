#!/usr/bin/env bash
set -e

# Load .env if mounted
if [ -f /app/.env ]; then
  set -a; . /app/.env; set +a
fi

PORT="${PORT:-8000}"

echo "===== Starting NexCode Django ====="
echo "Database: PostgreSQL"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

echo "Starting Gunicorn on port ${PORT}..."
exec gunicorn \
    --workers 3 \
    --timeout 60 \
    --bind 0.0.0.0:${PORT} \
    nexcode.wsgi:application
