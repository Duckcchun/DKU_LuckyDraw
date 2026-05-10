"""PostgreSQL 연결 대기 스크립트"""
import os
import sys
import time

import psycopg2


def wait_for_db():
    """DB가 준비될 때까지 대기"""
    db_config = {
        'dbname': os.environ.get('DB_NAME', 'lottodb'),
        'user': os.environ.get('DB_USER', 'lottouser'),
        'password': os.environ.get('DB_PASSWORD', 'lottopass'),
        'host': os.environ.get('DB_HOST', 'db'),
        'port': os.environ.get('DB_PORT', '5432'),
    }

    max_retries = 30
    retry_count = 0

    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(**db_config)
            conn.close()
            print("PostgreSQL is ready!")
            sys.exit(0)
        except psycopg2.OperationalError as e:
            retry_count += 1
            print(f"PostgreSQL not ready (attempt {retry_count}/{max_retries}): {e}")
            time.sleep(2)

    print("Could not connect to PostgreSQL after max retries")
    sys.exit(1)


if __name__ == '__main__':
    wait_for_db()
