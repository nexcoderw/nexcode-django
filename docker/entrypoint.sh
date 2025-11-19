#!/usr/bin/env bash
set -e

# Load .env if mounted
if [ -f /app/.env ]; then
  set -a; . /app/.env; set +a
fi

# Default environment variables (can be overridden)
PORT="${PORT:-8000}"
export DJANGO_DB="${DJANGO_DB:-postgres}"

echo "Starting NexCode Django App"
echo "Database mode: $DJANGO_DB"

# Run migrations & collectstatic (idempotent)
echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

# Start Gunicorn
echo "Starting Gunicorn on port ${PORT}..."
exec gunicorn \
    --workers 3 \
    --timeout 60 \
    --bind 0.0.0.0:${PORT} \
    nexcode.wsgi:application
