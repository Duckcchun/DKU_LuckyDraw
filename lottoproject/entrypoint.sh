#!/bin/bash

# DB가 준비될 때까지 대기
echo "Waiting for PostgreSQL..."
while ! python -c "
import psycopg2
try:
    conn = psycopg2.connect(
        dbname='$DB_NAME',
        user='$DB_USER',
        password='$DB_PASSWORD',
        host='$DB_HOST',
        port='$DB_PORT'
    )
    conn.close()
    exit(0)
except:
    exit(1)
" 2>/dev/null; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
done

echo "PostgreSQL is up - running migrations"

# 마이그레이션 실행
python manage.py makemigrations lotto
python manage.py migrate

# 관리자 계정 생성 (최초 실행시만)
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@dku.ac.kr', 'admin1234')
    print('Superuser created: admin / admin1234')
else:
    print('Superuser already exists')
"

# static 파일 수집
python manage.py collectstatic --noinput

# Gunicorn으로 서버 실행
echo "Starting Gunicorn..."
exec gunicorn lottoproject.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --access-logfile - \
    --error-logfile -
