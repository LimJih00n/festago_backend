# Festago Backend Deployment Guide

## Cloudtype 배포 가이드

### 1. Cloudtype에 프로젝트 연결

1. [Cloudtype](https://cloudtype.io/)에 로그인
2. "새 프로젝트" 클릭
3. GitHub 저장소 선택: `festago_backend`
4. 파이썬 버전 선택: `Python 3.11`

### 2. 환경변수 설정

Cloudtype 대시보드에서 다음 환경변수 추가:

#### 필수 환경변수

```bash
# Django 보안 설정
SECRET_KEY=your-super-secret-key-here-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=your-domain.cloudtype.app

# Frontend URL (CORS 설정)
FRONTEND_URL=https://your-netlify-site.netlify.app

# 데이터베이스 (Cloudtype에서 PostgreSQL 추가 시 자동 설정)
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

#### 선택 환경변수

```bash
# JWT 토큰 만료 시간 (분 단위)
JWT_ACCESS_TOKEN_LIFETIME=5
JWT_REFRESH_TOKEN_LIFETIME=1440

# 이메일 설정
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 3. 빌드 및 실행 설정

**Start Command:**
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

### 4. 데이터베이스 마이그레이션

Cloudtype에서 PostgreSQL 데이터베이스를 추가한 후:

```bash
# Cloudtype 터미널에서 실행
python manage.py migrate
python manage.py createsuperuser
```

### 5. 정적 파일 설정

프로덕션 환경에서 정적 파일을 제공하려면:

```bash
python manage.py collectstatic --noinput
```

## 로컬 개발 환경 설정

`.env` 파일 생성:

```bash
SECRET_KEY=django-insecure-dev-key-for-local-development
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
FRONTEND_URL=http://localhost:5173
```

## 주요 환경변수

### 필수
- `SECRET_KEY`: Django 보안 키
- `DEBUG`: 디버그 모드 (프로덕션에서는 False)
- `ALLOWED_HOSTS`: 허용된 호스트 (쉼표로 구분)
- `FRONTEND_URL`: 프론트엔드 URL (CORS 설정용)

### 선택
- `DATABASE_URL`: 데이터베이스 연결 URL (PostgreSQL, MySQL 등)
- `JWT_ACCESS_TOKEN_LIFETIME`: Access 토큰 만료 시간 (분)
- `JWT_REFRESH_TOKEN_LIFETIME`: Refresh 토큰 만료 시간 (분)

## 배포 체크리스트

- [ ] `SECRET_KEY` 변경
- [ ] `DEBUG=False` 설정
- [ ] `ALLOWED_HOSTS` 도메인 추가
- [ ] `FRONTEND_URL` 설정
- [ ] PostgreSQL 데이터베이스 연결
- [ ] 마이그레이션 실행
- [ ] Superuser 생성
- [ ] Static 파일 수집

## 테스트

로컬에서 프로덕션 설정 테스트:

```bash
# 환경변수 설정
export DEBUG=False
export SECRET_KEY=test-secret-key

# 서버 실행
python manage.py runserver
```

## 문제 해결

### CORS 에러
- `FRONTEND_URL` 환경변수가 올바른지 확인
- Netlify URL과 정확히 일치하는지 확인 (https 포함)

### 데이터베이스 연결 실패
- `DATABASE_URL` 형식 확인: `postgresql://user:pass@host:port/dbname`
- Cloudtype PostgreSQL 연결 정보 확인

### Static 파일 404
- `collectstatic` 명령 실행 확인
- `STATIC_ROOT` 설정 확인
