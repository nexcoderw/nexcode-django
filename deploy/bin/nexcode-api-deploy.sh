#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="nexcode"
PROJECT_USER="nexcode"
APP_ROOT="/var/www/${PROJECT_NAME}"
RELEASES_DIR="${APP_ROOT}/releases/api"
SHARED_DIR="${APP_ROOT}/shared/api"
SHARED_MEDIA_DIR="${APP_ROOT}/shared/media"
LIVE_LINK="${APP_ROOT}/api"
LOG_DIR="${APP_ROOT}/shared/logs"
PM2_CONFIG="${APP_ROOT}/shared/pm2/${PROJECT_NAME}-api.ecosystem.config.cjs"
REPO_URL="${REPO_URL:-https://github.com/nexcoderw/nexcode-django.git}"
DEFAULT_BRANCH="main"

REF="${1:-${DEFAULT_BRANCH}}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
TIMESTAMP="$(date +%Y%m%d%H%M%S)"
RELEASE_DIR="${RELEASES_DIR}/${TIMESTAMP}"
ENV_FILE="${SHARED_DIR}/.env.production"
PRUNE_SCRIPT="${APP_ROOT}/bin/${PROJECT_NAME}-prune-releases.sh"

if [[ "$(id -un)" != "${PROJECT_USER}" ]]; then
  echo "Run this script as ${PROJECT_USER}." >&2
  exit 1
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing production env file at ${ENV_FILE}." >&2
  exit 1
fi

if [[ ! -f "${PM2_CONFIG}" ]]; then
  echo "Missing PM2 config at ${PM2_CONFIG}." >&2
  exit 1
fi

set -a
source "${ENV_FILE}"
set +a

PORT="${PORT:-8000}"

mkdir -p "${RELEASES_DIR}" "${SHARED_DIR}" "${SHARED_MEDIA_DIR}" "${LOG_DIR}" "${APP_ROOT}/shared/pm2" "${APP_ROOT}/bin"

git clone --depth 1 --branch "${DEFAULT_BRANCH}" "${REPO_URL}" "${RELEASE_DIR}"
git -C "${RELEASE_DIR}" fetch --depth 1 origin "${REF}"
git -C "${RELEASE_DIR}" checkout --detach FETCH_HEAD

ln -sfn "${ENV_FILE}" "${RELEASE_DIR}/.env.production"
ln -sfn "${ENV_FILE}" "${RELEASE_DIR}/.env"
rm -rf "${RELEASE_DIR}/media"
ln -sfn "${SHARED_MEDIA_DIR}" "${RELEASE_DIR}/media"

"${PYTHON_BIN}" -m venv "${RELEASE_DIR}/venv"
"${RELEASE_DIR}/venv/bin/pip" install --upgrade pip setuptools wheel
"${RELEASE_DIR}/venv/bin/pip" install -r "${RELEASE_DIR}/requirements.txt"
chmod +x "${RELEASE_DIR}/venv/bin/gunicorn"

(
  cd "${RELEASE_DIR}"
  DJANGO_ENV=production PORT="${PORT}" "${RELEASE_DIR}/venv/bin/python" manage.py migrate --noinput
  DJANGO_ENV=production PORT="${PORT}" "${RELEASE_DIR}/venv/bin/python" manage.py collectstatic --noinput
  DJANGO_ENV=production PORT="${PORT}" "${RELEASE_DIR}/venv/bin/python" manage.py check --deploy
)

rm -rf "${RELEASE_DIR}/.git"

PREVIOUS_RELEASE=""
if [[ -L "${LIVE_LINK}" ]]; then
  PREVIOUS_RELEASE="$(readlink "${LIVE_LINK}")"
fi

ln -sfn "${RELEASE_DIR}" "${LIVE_LINK}"

rollback() {
  if [[ -n "${PREVIOUS_RELEASE}" ]]; then
    ln -sfn "${PREVIOUS_RELEASE}" "${LIVE_LINK}"
    pm2 startOrReload "${PM2_CONFIG}" --only "${PROJECT_NAME}-api" --update-env >/dev/null 2>&1 || true
  fi
}

if ! pm2 startOrReload "${PM2_CONFIG}" --only "${PROJECT_NAME}-api" --update-env; then
  rollback
  echo "PM2 reload failed. Live symlink was rolled back." >&2
  exit 1
fi

health_ok=false
for _ in {1..30}; do
  if curl --fail --silent --show-error "http://127.0.0.1:${PORT}/health/" >/dev/null; then
    health_ok=true
    break
  fi
  sleep 1
done

if [[ "${health_ok}" != "true" ]]; then
  rollback
  echo "Health check failed after deploy. Live symlink was rolled back." >&2
  exit 1
fi

pm2 save
"${PRUNE_SCRIPT}" "${RELEASES_DIR}"

echo "Deployed ${PROJECT_NAME} release ${TIMESTAMP} from ${REF}."
