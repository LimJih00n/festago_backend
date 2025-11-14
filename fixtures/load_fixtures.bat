@echo off
chcp 65001 > nul
REM 페스타고 MVP 테스트 데이터 Import 스크립트 (Windows)
REM 사용법: fixtures\load_fixtures.bat

echo ========================================
echo 페스타고 MVP 테스트 데이터 Import
echo ========================================
echo.

REM Django 프로젝트 경로 확인
if not exist "manage.py" (
    echo ❌ 오류: manage.py를 찾을 수 없습니다.
    echo 💡 Django 프로젝트 루트 디렉토리에서 실행하세요.
    echo.
    echo 올바른 경로:
    echo   cd festago-backend
    echo   ..\fixtures\load_fixtures.bat
    pause
    exit /b 1
)

echo ✅ Django 프로젝트 확인됨
echo.

REM fixtures 파일 확인
if not exist "fixtures\users.json" (
    if not exist "..\fixtures\users.json" (
        echo ❌ 오류: fixtures 파일을 찾을 수 없습니다.
        echo 💡 fixtures 폴더가 프로젝트 내부 또는 상위 디렉토리에 있어야 합니다.
        pause
        exit /b 1
    )
)

REM fixtures 경로 설정
if exist "fixtures\users.json" (
    set FIXTURES_PATH=fixtures
) else (
    set FIXTURES_PATH=..\fixtures
)

echo ✅ Fixtures 파일 확인됨: %FIXTURES_PATH%
echo.

REM Import 시작
echo 🚀 데이터 Import 시작...
echo.

REM Users import
echo 1️⃣  Users 데이터 import 중...
python manage.py loaddata %FIXTURES_PATH%\users.json

if %errorlevel% neq 0 (
    echo    ❌ Users import 실패
    pause
    exit /b 1
)
echo    ✅ Users import 완료
echo.

REM Events import
echo 2️⃣  Events 데이터 import 중...
python manage.py loaddata %FIXTURES_PATH%\events.json

if %errorlevel% neq 0 (
    echo    ❌ Events import 실패
    pause
    exit /b 1
)
echo    ✅ Events import 완료
echo.

REM 최종 확인
echo ========================================
echo 📊 Import 완료
echo ========================================
echo.

echo 🎉 완료!
echo.
echo 다음 단계:
echo   1. Django Admin 확인: http://localhost:8000/admin
echo      - Username: admin
echo      - Password: test1234
echo.
echo   2. API 확인: http://localhost:8000/api/events/
echo.
echo   3. 서버 실행 (아직 실행 안 했다면):
echo      python manage.py runserver
echo.

pause
