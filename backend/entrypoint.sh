#!/bin/sh
set -e

cd /app

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py ensure_demo_seed

exec "$@"
