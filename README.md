# 페스타고 Backend (Django REST API)

**프로젝트**: 페스타고 - 지역 축제 플랫폼
**기술 스택**: Django 4.2 + Django REST Framework + JWT

---

## 🚀 빠른 시작

### 1. 가상환경 생성 및 활성화

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 마이그레이션

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 테스트 데이터 로드

```bash
python manage.py loaddata fixtures/users.json
python manage.py loaddata fixtures/events.json
```

### 5. 서버 실행

```bash
python manage.py runserver
```

서버가 실행되면: http://localhost:8000

---

## 📊 테스트 계정

### Admin
```
Username: admin
Password: test1234
URL: http://localhost:8000/admin
```

### 일반 사용자
```
Username: testuser1
Password: test1234
```

---

## 🔌 API 엔드포인트

### 인증
```
POST   /api/auth/login/      # 로그인 (JWT 발급)
POST   /api/auth/refresh/    # 토큰 갱신
```

### 사용자
```
POST   /api/users/signup/    # 회원가입
GET    /api/users/me/        # 내 정보
PATCH  /api/users/me/        # 내 정보 수정
```

### 이벤트
```
GET    /api/events/          # 이벤트 목록
GET    /api/events/1/        # 이벤트 상세
GET    /api/events/map/      # 지도용 (좌표만)

필터링:
GET    /api/events/?category=festival
GET    /api/events/?location=서울
GET    /api/events/?search=불꽃
```

---

## 🗄️ 데이터베이스

- SQLite3 (개발용)
- 테스트 데이터:
  - Users: 5명
  - Events: 30개

---

## 📁 프로젝트 구조

```
festago-backend/
├── config/              # Django 설정
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/              # 사용자 앱
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── events/             # 이벤트 앱
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── fixtures/           # 테스트 데이터
│   ├── users.json
│   └── events.json
├── manage.py
└── requirements.txt
```

---

## 🧪 테스트

### API 테스트 (curl)
```bash
# 이벤트 목록
curl http://localhost:8000/api/events/

# 로그인
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser1","password":"test1234"}'
```

### Django Shell
```bash
python manage.py shell
```

```python
from events.models import Event
from users.models import User

# 데이터 확인
Event.objects.count()  # 30
User.objects.count()   # 5
```

---

## 🔧 관리 명령어

```bash
# 슈퍼유저 생성
python manage.py createsuperuser

# 마이그레이션 파일 생성
python manage.py makemigrations

# 마이그레이션 적용
python manage.py migrate

# 정적 파일 수집
python manage.py collectstatic

# 테스트 실행
python manage.py test
```

---

## ⚙️ 환경 변수 (.env)

프로덕션에서는 `.env` 파일 사용:

```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://...
```

---

## 🚀 배포 (Render)

1. GitHub에 push
2. Render에서 Web Service 생성
3. 환경 변수 설정
4. 자동 배포

---

## 📚 문서

- Django: https://docs.djangoproject.com/
- DRF: https://www.django-rest-framework.org/
- JWT: https://django-rest-framework-simplejwt.readthedocs.io/

---

**작성자**: Claude
**생성일**: 2025-10-27
