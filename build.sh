#!/usr/bin/env bash
# Render 빌드 스크립트
# exit on error
set -o errexit

echo "=== Festago Backend Build Script ==="

# 1. 패키지 설치
echo "[1/5] Installing dependencies..."
pip install -r requirements.txt

# 2. static 파일 수집
echo "[2/5] Collecting static files..."
python manage.py collectstatic --no-input

# 3. 데이터베이스 마이그레이션
echo "[3/5] Running migrations..."
python manage.py migrate

# 4. 이벤트 데이터 import (CSV/Excel)
echo "[4/5] Importing event data..."
python manage.py import_mokkoji_events

# 5. 파트너 샘플 데이터 생성 (없는 경우에만)
echo "[5/5] Generating sample partner data if needed..."
python manage.py generate_sample_data_if_empty

echo "=== Build Complete! ==="
