#!/bin/sh
set -eu

mkdir -p /app/config /app/data /app/logs /app/backups /home/r20/.okx /home/r20/.bypy /home/r20/.npm-global
touch "${R20_ENV_FILE:-/app/config/.env}"
chmod 0700 /home/r20/.okx /home/r20/.bypy /home/r20/.npm-global
chmod 0600 "${R20_ENV_FILE:-/app/config/.env}"

exec "$@"
