#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="${PROJECT_NAME:-nexcode}"
RELEASES_DIR="${1:-/var/www/${PROJECT_NAME}/releases/api}"
KEEP_RELEASES="${KEEP_RELEASES:-3}"

if [[ ! -d "${RELEASES_DIR}" ]]; then
  exit 0
fi

mapfile -t releases < <(find "${RELEASES_DIR}" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort -r)

if (( ${#releases[@]} <= KEEP_RELEASES )); then
  exit 0
fi

for release in "${releases[@]:KEEP_RELEASES}"; do
  rm -rf "${RELEASES_DIR}/${release}"
done
