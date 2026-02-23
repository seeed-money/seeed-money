#!/bin/sh
set -e

#uv 가상환경 경로를 PATH 맨 앞에 추가 (이게 가장 먼저 실행되어야 함)
export PATH="/app/.venv/bin:$PATH"

echo "--- Installed Packages ---"
pip list || echo "pip not found"
echo "--- Python Path ---"
which python
echo "--------------------------"

python /app/manage.py makemigrations --noinput
python /app/manage.py migrate

#Todo
# gunicorn 대신 임시로 python으로 실행 (개발용)
#gunicorn --bind 0.0.0.0:8000 config.wsgi:application --workers 2
python manage.py runserver 0.0.0.0:8000