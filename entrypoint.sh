#!/usr/bin/env bash
set -euo pipefail

# Wait for DB (optional) - user can comment if using sqlite
wait_for_db() {
  if [ -n "${POSTGRES_HOST:-}" ] && [ -n "${POSTGRES_PORT:-}" ]; then
    echo "Waiting for Postgres at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
    for i in $(seq 1 30); do
      if nc -z ${POSTGRES_HOST} ${POSTGRES_PORT}; then
        echo "Postgres reachable"
        return 0
      fi
      sleep 1
    done
    echo "Postgres not reachable after 30s"
    return 1
  fi
}

# Run optionally
wait_for_db || true

# Collect static files (won't fail if settings use sqlite or different static)
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Start gunicorn
# Number of workers: recommended (2 x $NUM_CPU) + 1 — we keep it configurable via env
NUM_WORKERS=${GUNICORN_WORKERS:-3}
echo "Starting gunicorn with ${NUM_WORKERS} workers"
exec gunicorn nexcode.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers ${NUM_WORKERS} \
  --log-level info \
  --access-logfile '-' \
  --error-logfile '-'
