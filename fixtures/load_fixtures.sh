#!/bin/bash

# 페스타고 MVP 테스트 데이터 Import 스크립트
# 사용법: bash fixtures/load_fixtures.sh

echo "========================================"
echo "페스타고 MVP 테스트 데이터 Import"
echo "========================================"
echo ""

# Django 프로젝트 경로 확인
if [ ! -f "manage.py" ]; then
    echo "❌ 오류: manage.py를 찾을 수 없습니다."
    echo "💡 Django 프로젝트 루트 디렉토리에서 실행하세요."
    echo ""
    echo "올바른 경로:"
    echo "  cd festago-backend"
    echo "  bash ../fixtures/load_fixtures.sh"
    exit 1
fi

echo "✅ Django 프로젝트 확인됨"
echo ""

# fixtures 파일 확인
if [ ! -f "fixtures/users.json" ] && [ ! -f "../fixtures/users.json" ]; then
    echo "❌ 오류: fixtures 파일을 찾을 수 없습니다."
    echo "💡 fixtures 폴더가 프로젝트 내부 또는 상위 디렉토리에 있어야 합니다."
    exit 1
fi

# fixtures 경로 설정
if [ -f "fixtures/users.json" ]; then
    FIXTURES_PATH="fixtures"
else
    FIXTURES_PATH="../fixtures"
fi

echo "✅ Fixtures 파일 확인됨: $FIXTURES_PATH"
echo ""

# 기존 데이터 확인
echo "📊 기존 데이터 확인 중..."
EXISTING_EVENTS=$(python manage.py shell -c "from events.models import Event; print(Event.objects.count())" 2>/dev/null)
EXISTING_USERS=$(python manage.py shell -c "from users.models import User; print(User.objects.count())" 2>/dev/null)

echo "   현재 Events: ${EXISTING_EVENTS:-0}개"
echo "   현재 Users: ${EXISTING_USERS:-0}개"
echo ""

# 데이터가 있으면 경고
if [ "$EXISTING_EVENTS" != "0" ] || [ "$EXISTING_USERS" != "0" ]; then
    echo "⚠️  경고: 이미 데이터가 존재합니다."
    echo ""
    echo "옵션:"
    echo "  1) 기존 데이터 유지하고 추가 import (중복 가능)"
    echo "  2) 기존 데이터 삭제 후 import"
    echo "  3) 취소"
    echo ""
    read -p "선택하세요 (1/2/3): " choice

    case $choice in
        1)
            echo "✅ 기존 데이터 유지하고 진행합니다."
            ;;
        2)
            echo "⚠️  기존 데이터를 삭제합니다..."
            python manage.py shell -c "from events.models import Event; from users.models import User; Event.objects.all().delete(); User.objects.all().delete(); print('✅ 삭제 완료')"
            ;;
        3)
            echo "❌ 취소되었습니다."
            exit 0
            ;;
        *)
            echo "❌ 잘못된 선택입니다."
            exit 1
            ;;
    esac
    echo ""
fi

# Import 시작
echo "🚀 데이터 Import 시작..."
echo ""

# Users import
echo "1️⃣  Users 데이터 import 중..."
python manage.py loaddata $FIXTURES_PATH/users.json

if [ $? -eq 0 ]; then
    echo "   ✅ Users import 완료"
else
    echo "   ❌ Users import 실패"
    exit 1
fi
echo ""

# Events import
echo "2️⃣  Events 데이터 import 중..."
python manage.py loaddata $FIXTURES_PATH/events.json

if [ $? -eq 0 ]; then
    echo "   ✅ Events import 완료"
else
    echo "   ❌ Events import 실패"
    exit 1
fi
echo ""

# 최종 확인
echo "========================================"
echo "📊 Import 결과"
echo "========================================"

TOTAL_EVENTS=$(python manage.py shell -c "from events.models import Event; print(Event.objects.count())" 2>/dev/null)
TOTAL_USERS=$(python manage.py shell -c "from users.models import User; print(User.objects.count())" 2>/dev/null)

echo "✅ Events: ${TOTAL_EVENTS}개"
echo "✅ Users: ${TOTAL_USERS}개"
echo ""

echo "🎉 완료!"
echo ""
echo "다음 단계:"
echo "  1. Django Admin 확인: http://localhost:8000/admin"
echo "     - Username: admin"
echo "     - Password: test1234"
echo ""
echo "  2. API 확인: http://localhost:8000/api/events/"
echo ""
echo "  3. 서버 실행 (아직 실행 안 했다면):"
echo "     python manage.py runserver"
echo ""
