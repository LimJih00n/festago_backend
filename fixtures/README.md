# 페스타고 MVP 테스트 데이터

**목적**: Django 개발 및 테스트를 위한 샘플 데이터
**생성일**: 2025-10-27

---

## 📦 포함된 데이터

### 1. events.json
```
30개의 축제/행사 데이터

카테고리별:
- 축제 (festival): 18개
- 공연 (concert): 7개
- 전시 (exhibition): 3개
- 팝업스토어 (popup): 2개

지역별:
- 서울/경기: 12개
- 부산/경남: 3개
- 대구/경북: 3개
- 광주/전라: 4개
- 대전/충청: 2개
- 강원: 3개
- 제주: 1개
- 기타: 2개

날짜별:
- 2025년 9월~12월: 15개
- 2026년 1월~8월: 15개

모든 데이터에 좌표 포함 ✅
```

### 2. users.json
```
5명의 테스트 사용자

계정 정보:
1. admin / test1234          (관리자)
2. testuser1 / test1234      (일반 사용자 - 김철수)
3. testuser2 / test1234      (일반 사용자 - 이영희)
4. partner1 / test1234       (사업자 - 박사업)
5. partner2 / test1234       (사업자 - 최장사)

모든 비밀번호: test1234
```

---

## 🚀 사용 방법

### 1. Django 프로젝트 준비

먼저 Django 프로젝트가 설정되어 있어야 합니다.

```bash
# festago-backend 디렉토리로 이동
cd festago-backend

# 가상환경 활성화
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 마이그레이션 실행
python manage.py makemigrations
python manage.py migrate
```

---

### 2. Fixtures 복사

fixtures 폴더를 Django 프로젝트 안으로 복사합니다.

```bash
# 프로젝트 루트에 fixtures 폴더가 있도록
festago-backend/
├── fixtures/
│   ├── events.json
│   ├── users.json
│   └── README.md
├── manage.py
├── config/
└── ...
```

또는 직접 경로를 지정할 수도 있습니다.

---

### 3. 데이터 Import

#### 방법 1: 한 번에 모두 import (권장)
```bash
python manage.py loaddata fixtures/users.json fixtures/events.json
```

#### 방법 2: 개별 import
```bash
# 사용자 먼저
python manage.py loaddata fixtures/users.json

# 그 다음 이벤트
python manage.py loaddata fixtures/events.json
```

#### 성공 메시지
```
Installed 5 object(s) from 1 fixture(s)
Installed 30 object(s) from 1 fixture(s)
```

---

### 4. 확인

#### Django Admin에서 확인
```bash
# 서버 실행
python manage.py runserver

# 브라우저 접속
http://localhost:8000/admin

# 로그인
Username: admin
Password: test1234
```

#### API에서 확인
```bash
# 이벤트 목록
http://localhost:8000/api/events/

# 지도용 데이터
http://localhost:8000/api/events/map/

# 특정 이벤트
http://localhost:8000/api/events/1/
```

#### Django Shell에서 확인
```bash
python manage.py shell
```

```python
from events.models import Event
from users.models import User

# 전체 개수
Event.objects.count()  # 30
User.objects.count()   # 5

# 카테고리별
Event.objects.filter(category='festival').count()  # 18
Event.objects.filter(category='concert').count()   # 7

# 좌표 있는 이벤트
Event.objects.filter(latitude__isnull=False).count()  # 30 (100%)

# 11월 이벤트
from datetime import date
Event.objects.filter(start_date__month=11).count()

# 서울 이벤트
Event.objects.filter(location__contains='서울').count()
```

---

## 🗑️ 데이터 삭제

테스트 후 데이터를 삭제하려면:

```bash
python manage.py shell
```

```python
from events.models import Event
from users.models import User

# 이벤트만 삭제
Event.objects.all().delete()

# 사용자만 삭제 (관리자 제외)
User.objects.exclude(username='admin').delete()

# 모두 삭제
Event.objects.all().delete()
User.objects.all().delete()

exit()
```

또는 DB를 완전히 초기화:

```bash
# SQLite인 경우
rm db.sqlite3
python manage.py migrate
```

---

## 🎨 데이터 특징

### 실제 지역 기반
```
✅ 실제 존재하는 지역명
✅ 정확한 좌표 (위도/경도)
✅ 실제 주소
```

### 다양한 카테고리
```
✅ 축제: 지역 축제, 음식 축제, 문화 축제
✅ 공연: 재즈, 록, 클래식, 거리 공연
✅ 전시: 미술 전시, 영화제, 디자인 페어
✅ 팝업: 브랜드 팝업스토어
```

### 시간대 분포
```
✅ 과거 (2025년 9월~10월): 테스트용
✅ 현재 (2025년 11월~12월): 메인 데이터
✅ 미래 (2026년 1월~8월): 예정 행사
```

### 이미지 URL
```
⚠️ Unsplash 무료 이미지 사용
- 실제 서비스에서는 Cloudinary 등 사용
- 개발/테스트용으로만 사용
```

---

## 🧪 테스트 시나리오

### 1. 사용자 로그인 테스트
```
1. testuser1으로 로그인
2. 축제 목록 확인
3. 축제 상세 페이지 확인
4. 북마크 추가/삭제
```

### 2. 지도 기능 테스트
```
1. /api/events/map/ 호출
2. 30개 이벤트의 좌표 확인
3. 카카오맵에 마커 표시
4. 서울/부산 등 지역별 필터링
```

### 3. 필터링 테스트
```
1. 카테고리: festival, concert, exhibition, popup
2. 지역: 서울시, 부산시, 제주도 등
3. 날짜: 2025-11, 2026-04 등
4. 검색: "불꽃", "재즈", "커피" 등
```

### 4. 사업자 기능 테스트 (선택)
```
1. partner1으로 로그인
2. 사업자 프로필 등록
3. 축제에 지원 신청
4. 지원 내역 확인
```

---

## ⚠️ 주의사항

### 비밀번호 보안
```
⚠️ 모든 테스트 계정의 비밀번호: test1234
⚠️ 실제 프로덕션에서는 절대 사용 금지!
⚠️ 개발/테스트 환경에서만 사용
```

### 이미지 URL
```
⚠️ Unsplash 이미지는 테스트용
⚠️ 실제 서비스에서는 저작권 주의
⚠️ Cloudinary 등 이미지 호스팅 사용 권장
```

### 데이터 정확성
```
ℹ️ 임의로 생성된 테스트 데이터
ℹ️ 실제 축제와 날짜가 다를 수 있음
ℹ️ MVP 테스트 목적으로만 사용
```

---

## 🔄 데이터 재import

이미 import된 상태에서 다시 import하면 중복 에러가 발생합니다.

### 해결 방법:
```bash
# 1. 기존 데이터 삭제
python manage.py shell
>>> from events.models import Event
>>> Event.objects.all().delete()
>>> exit()

# 2. 재import
python manage.py loaddata fixtures/events.json
```

---

## 📊 데이터 통계

### Events (30개)
```
카테고리:
- festival: 18개 (60%)
- concert: 7개 (23%)
- exhibition: 3개 (10%)
- popup: 2개 (7%)

지역 (상위 5개):
- 서울: 9개
- 경기: 3개
- 부산: 2개
- 강원: 3개
- 전라: 4개

날짜:
- 2025년: 15개
- 2026년: 15개

좌표:
- 100% (30/30개)
```

### Users (5명)
```
타입:
- 관리자: 1명 (admin)
- 일반 사용자: 2명 (testuser1, testuser2)
- 사업자: 2명 (partner1, partner2)

권한:
- 슈퍼유저: 1명
- 일반 유저: 4명
```

---

## 💡 Tips

### 빠른 확인
```bash
# 이벤트 개수
python manage.py shell -c "from events.models import Event; print(Event.objects.count())"

# 사용자 목록
python manage.py shell -c "from users.models import User; [print(u.username, u.user_type) for u in User.objects.all()]"
```

### Admin에서 빠른 편집
```
http://localhost:8000/admin/events/event/
에서 이벤트 추가/수정/삭제 가능
```

### API 테스트
```bash
# Postman 또는 curl 사용
curl http://localhost:8000/api/events/

# jq로 예쁘게 출력 (jq 설치 필요)
curl http://localhost:8000/api/events/ | jq
```

---

## 🎯 다음 단계

1. ✅ fixtures import 완료
2. ⬜ Django Admin에서 데이터 확인
3. ⬜ React에서 API 호출 테스트
4. ⬜ 지도에 마커 표시 테스트
5. ⬜ 필터링/검색 기능 테스트
6. ⬜ 북마크 기능 테스트

---

## 📚 관련 문서

- **빠른 시작 가이드**: `docs/07_빠른_시작_가이드.md`
- **아키텍처**: `docs/06_React_Django_분리_아키텍처.md`
- **README**: `docs/README.md`

---

**작성자**: Claude
**생성일**: 2025-10-27
**데이터 개수**: Events 30개, Users 5명
