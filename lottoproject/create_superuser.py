"""관리자 계정 자동 생성 스크립트"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lottoproject.settings')
django.setup()

try:
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@dku.ac.kr', 'admin1234')
        print('Superuser created: admin / admin1234')
    else:
        print('Superuser already exists')
except Exception as e:
    print(f'Warning: Could not create superuser: {e}')
    sys.exit(0)
