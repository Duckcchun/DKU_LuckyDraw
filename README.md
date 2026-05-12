# DKU 6/45 LuckyDraw - 로또 웹 애플리케이션

## 프로젝트 개요

Django와 Docker를 사용하여 개발한 6/45 Lotto 웹 애플리케이션입니다.  
일반 사용자는 복권 구매 및 당첨 확인이 가능하며, 관리자는 판매 내역 확인, 추첨, 당첨 내역 확인 기능을 제공합니다.

**배포 URL:** https://dkuluckydraw-production.up.railway.app/

---

## 1. 시스템 설계

### 1.1 시스템 아키텍처

#### 로컬 개발 환경 (Docker Multi-Container)

```
┌─────────────────────────────────────────────────────┐
│                    Docker Network                     │
│                                                       │
│  ┌──────────┐    ┌──────────────┐    ┌───────────┐  │
│  │  Nginx   │───▶│ Django +     │───▶│ PostgreSQL│  │
│  │ (Port 80)│    │  Gunicorn    │    │ (Port 5432)│  │
│  └──────────┘    └──────────────┘    └───────────┘  │
│   [Container1]     [Container2]       [Container3]   │
└─────────────────────────────────────────────────────┘
         │
    [Client Browser]
```

#### 배포 환경 (Railway)

```
┌───────────────────────────────────────┐
│              Railway Cloud             │
│                                        │
│  ┌──────────────┐    ┌───────────┐   │
│  │ Django +     │───▶│ PostgreSQL│   │
│  │ Gunicorn     │    │ (Railway) │   │
│  │ + WhiteNoise │    └───────────┘   │
│  └──────────────┘                     │
└───────────────────────────────────────┘
         │
    [Client Browser]
    https://dkuluckydraw-production.up.railway.app/
```

### 1.2 기술 스택

| 구분 | 기술 | 버전 |
|------|------|------|
| Backend | Django (Python) | 5.1 |
| Database | PostgreSQL | 15 |
| Web Server (로컬) | Nginx | 1.25 |
| WSGI Server | Gunicorn | 22.0 |
| 정적파일 (배포) | WhiteNoise | 6.6 |
| Frontend | Bootstrap | 5.3 |
| Container (로컬) | Docker + Docker Compose | Latest |
| 배포 플랫폼 | Railway | - |
| DB URL 파싱 | dj-database-url | 2.1 |

### 1.3 데이터 모델 설계 (ERD)

```
┌─────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│   User (Django)  │       │    LottoRound    │       │   DrawResult    │
├─────────────────┤       ├──────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)          │       │ id (PK)         │
│ username        │       │ round_number     │◀──────│ lotto_round (FK)│
│ email           │       │ is_active        │       │ number_1~6      │
│ password        │       │ created_at       │       │ bonus_number    │
│ is_staff        │       │ draw_date        │       │ drawn_at        │
└────────┬────────┘       └────────┬─────────┘       └─────────────────┘
         │                         │
         │    ┌────────────────────┘
         │    │
         ▼    ▼
┌──────────────────────┐
│     LottoTicket      │
├──────────────────────┤
│ id (PK)              │
│ user (FK → User)     │
│ lotto_round (FK)     │
│ number_1 ~ number_6  │
│ purchase_type        │
│ purchased_at         │
│ prize_rank           │
└──────────────────────┘
```

### 1.4 주요 기능

#### 일반 사용자
- **회원가입/로그인/로그아웃**: Django 인증 시스템 활용
- **자동번호 구매**: 1~45 중 랜덤 6개 번호 자동 생성 (1~5장)
- **수동번호 구매**: 사용자가 직접 6개 번호 선택 (중복 검증)
- **내 티켓 확인**: 구매한 티켓 목록 조회
- **당첨 확인**: 추첨 완료된 회차의 당첨 결과 확인

#### 관리자
- **대시보드**: 현재 회차, 판매량, 사용자 수 등 통계
- **판매 내역**: 회차별 전체 판매 내역 조회 (필터링)
- **추첨 실행**: 현재 회차 추첨 진행 (7개 번호 생성)
- **당첨 내역**: 전체 회차별 당첨자 목록 확인

### 1.5 당첨 규칙

| 등수 | 조건 | 설명 |
|------|------|------|
| 1등 | 6개 번호 모두 일치 | 당첨번호 6개 전부 맞춤 |
| 2등 | 5개 + 보너스번호 일치 | 5개 맞추고 보너스번호도 일치 |
| 3등 | 5개 번호 일치 | 당첨번호 5개 맞춤 |
| 4등 | 4개 번호 일치 | 당첨번호 4개 맞춤 |
| 5등 | 3개 번호 일치 | 당첨번호 3개 맞춤 |

---

## 2. 프로젝트 구조

```
DKU_LuckyDraw/
├── docker-compose.yml          # Docker Compose 설정 (로컬 개발용)
├── railway.toml                # Railway 배포 설정
├── requirements.txt            # Python 의존성 (루트)
├── .env.example                # 환경변수 샘플
├── .gitignore                  # Git 무시 파일
├── README.md                   # 프로젝트 보고서
│
├── lottoproject/               # Django 프로젝트 (Railway Root Directory)
│   ├── Dockerfile.local        # Docker 컨테이너 설정 (로컬용)
│   ├── entrypoint.sh           # Docker 컨테이너 시작 스크립트
│   ├── wait_for_db.py          # PostgreSQL 연결 대기 스크립트
│   ├── create_superuser.py     # 관리자 계정 자동 생성 스크립트
│   ├── requirements.txt        # Python 의존성
│   ├── runtime.txt             # Python 버전 지정
│   ├── Procfile                # 프로세스 정의
│   ├── manage.py               # Django 관리 명령어
│   │
│   ├── lottoproject/           # 프로젝트 설정
│   │   ├── settings.py         # Django 설정 (DB, CSRF, WhiteNoise 등)
│   │   ├── urls.py             # URL 라우팅
│   │   └── wsgi.py             # WSGI 설정
│   │
│   ├── lotto/                  # 로또 앱
│   │   ├── models.py           # 데이터 모델 (LottoRound, LottoTicket, DrawResult)
│   │   ├── views.py            # 뷰 로직 (사용자/관리자 기능)
│   │   ├── forms.py            # 폼 정의 (회원가입, 수동번호)
│   │   ├── urls.py             # 앱 URL
│   │   ├── urls_accounts.py    # 인증 URL
│   │   ├── admin.py            # Django Admin 설정
│   │   └── apps.py             # 앱 설정
│   │
│   ├── templates/              # HTML 템플릿
│   │   ├── base.html           # 기본 레이아웃 (Bootstrap 5)
│   │   ├── registration/       # 인증 관련
│   │   │   ├── login.html
│   │   │   └── signup.html
│   │   └── lotto/              # 로또 기능
│   │       ├── home.html
│   │       ├── purchase_auto.html
│   │       ├── purchase_manual.html
│   │       ├── purchase_result.html
│   │       ├── my_tickets.html
│   │       ├── check_results.html
│   │       ├── admin_dashboard.html
│   │       ├── admin_sales.html
│   │       ├── admin_draw.html
│   │       ├── admin_draw_result.html
│   │       └── admin_winners.html
│   │
│   └── static/                 # 정적 파일
│       ├── css/.gitkeep
│       └── js/.gitkeep
│
└── nginx/                      # Nginx 설정 (로컬용)
    ├── Dockerfile              # Nginx 컨테이너 설정
    └── nginx.conf              # Nginx 리버스 프록시 설정
```

---

## 3. 구현 과정

### 3.1 Django 프로젝트 생성 및 모델 설계

1. Django 프로젝트(`lottoproject`) 및 앱(`lotto`) 생성
2. 데이터 모델 설계: `LottoRound`, `LottoTicket`, `DrawResult`
3. PostgreSQL 데이터베이스 연동 (`dj-database-url` 활용)

### 3.2 사용자 인증 시스템

1. Django 내장 `User` 모델 활용
2. `UserCreationForm` 확장하여 회원가입 폼 구현
3. Django `LoginView`, `LogoutView` 활용
4. `@login_required` 데코레이터로 접근 제어
5. `@user_passes_test(is_admin)` 데코레이터로 관리자 권한 확인

### 3.3 복권 구매 기능

1. **자동 구매**: `random.sample(range(1, 46), 6)`으로 중복 없는 6개 번호 생성
2. **수동 구매**: 폼 검증으로 1~45 범위, 중복 번호 체크
3. 구매 결과 즉시 표시

### 3.4 추첨 및 당첨 확인

1. **추첨**: 7개 번호 생성 (6개 당첨번호 + 1개 보너스번호)
2. **당첨 판정**: 각 티켓과 당첨번호 비교하여 등수 산출
3. 추첨 후 해당 회차 판매 자동 종료, 새 회차 자동 생성

### 3.5 Docker Multi-Container 구성 (로컬 개발)

| 서비스 | 이미지 | 역할 |
|--------|--------|------|
| `db` | postgres:15-alpine | 데이터 저장소 |
| `web` | python:3.11-slim (커스텀) | Django 애플리케이션 서버 |
| `nginx` | nginx:1.25-alpine (커스텀) | 리버스 프록시 + 정적파일 서빙 |

**컨테이너 간 통신:**
- `nginx` → `web` (HTTP 프록시, port 8000)
- `web` → `db` (PostgreSQL 연결, port 5432)
- 외부 접근: `localhost:80` → Nginx

### 3.6 Railway 클라우드 배포

1. Railway에 GitHub 레포 연결
2. PostgreSQL 서비스 추가 및 `DATABASE_URL` 환경변수 연결
3. Nixpacks 빌더로 자동 빌드 (Python 감지)
4. WhiteNoise로 정적파일 서빙 (Nginx 불필요)
5. CSRF 설정 및 ALLOWED_HOSTS 설정

---

## 4. 실행 방법

### 4.1 배포 환경 (Railway - 즉시 접속 가능)

**URL:** https://dkuluckydraw-production.up.railway.app/

| 구분 | 아이디 | 비밀번호 |
|------|--------|----------|
| 관리자 | admin | admin1234 |

> 일반 사용자는 회원가입으로 생성 가능

### 4.2 로컬 실행 (Docker)

#### 사전 요구사항
- Docker & Docker Compose 설치

#### 실행 명령

```bash
# 1. 레포지토리 클론
git clone https://github.com/Duckcchun/DKU_LuckyDraw.git
cd DKU_LuckyDraw

# 2. Docker Compose로 빌드 및 실행
docker-compose up --build

# 3. 브라우저에서 접속
# http://localhost
```

#### 기본 계정

| 구분 | 아이디 | 비밀번호 |
|------|--------|----------|
| 관리자 | admin | admin1234 |

> 관리자 계정은 최초 실행 시 자동 생성됩니다.

#### 종료

```bash
docker-compose down          # 컨테이너 종료
docker-compose down -v       # 컨테이너 + 볼륨(DB 데이터) 삭제
```

---

## 5. 테스트 결과

### 5.1 기능 테스트 시나리오

| # | 테스트 항목 | 기대 결과 | 상태 |
|---|-------------|-----------|------|
| 1 | 회원가입 | 사용자 생성 후 자동 로그인 | ✅ |
| 2 | 로그인/로그아웃 | 정상 인증 처리 | ✅ |
| 3 | 자동번호 구매 (1~5장) | 중복 없는 6개 번호 생성 및 저장 | ✅ |
| 4 | 수동번호 구매 | 입력값 검증 (범위, 중복) 후 저장 | ✅ |
| 5 | 내 티켓 확인 | 구매한 티켓 목록 표시 | ✅ |
| 6 | 관리자 - 판매 내역 | 전체/회차별 판매 조회 | ✅ |
| 7 | 관리자 - 추첨 실행 | 7개 번호 생성, 당첨 자동 판정 | ✅ |
| 8 | 관리자 - 당첨 내역 | 등수별 당첨자 목록 표시 | ✅ |
| 9 | 사용자 - 당첨 확인 | 내 티켓의 당첨 결과 표시 | ✅ |
| 10 | Docker 컨테이너 실행 | 3개 컨테이너 정상 기동 | ✅ |
| 11 | Railway 배포 | 클라우드 환경에서 정상 동작 | ✅ |
| 12 | 비로그인 접근 제한 | 구매 페이지 접근 시 로그인 리다이렉트 | ✅ |
| 13 | 일반 사용자 관리자 접근 차단 | 리다이렉트 처리 | ✅ |

### 5.2 테스트 수행 과정

```
[로컬 Docker 환경]
1. docker-compose up --build로 서비스 기동
2. http://localhost 접속 → 홈페이지 정상 출력 확인
3. 회원가입(testuser) → 자동 로그인 확인
4. 자동구매 3장 → 번호 생성 확인 (모두 1~45, 중복 없음)
5. 수동구매 (1,2,3,4,5,6) → 정상 저장 확인
6. 수동구매 중복번호 (1,1,2,3,4,5) → 에러 메시지 확인
7. admin 로그인 → 관리자 대시보드 접근 확인
8. 판매 내역 → 4장 판매 확인 (자동3, 수동1)
9. 추첨 실행 → 당첨번호 7개 생성 확인
10. 당첨 내역 → 등수별 당첨자 표시 확인
11. testuser 로그인 → 당첨 확인 페이지에서 결과 표시 확인

[Railway 배포 환경]
12. https://dkuluckydraw-production.up.railway.app/ 접속 확인
13. 회원가입/로그인 기능 정상 동작 확인
14. 관리자 추첨 기능 정상 동작 확인
```

---

## 6. URL 구조

| URL | 기능 | 접근 권한 |
|-----|------|-----------|
| `/` | 홈페이지 | 전체 |
| `/accounts/signup/` | 회원가입 | 비로그인 |
| `/accounts/login/` | 로그인 | 비로그인 |
| `/accounts/logout/` | 로그아웃 | 로그인 |
| `/purchase/auto/` | 자동 구매 | 로그인 |
| `/purchase/manual/` | 수동 구매 | 로그인 |
| `/my-tickets/` | 내 티켓 | 로그인 |
| `/results/` | 당첨 확인 | 로그인 |
| `/manager/` | 관리자 대시보드 | 관리자 |
| `/manager/sales/` | 판매 내역 | 관리자 |
| `/manager/draw/` | 추첨 실행 | 관리자 |
| `/manager/draw/<round>/` | 추첨 결과 상세 | 관리자 |
| `/manager/winners/` | 당첨 내역 | 관리자 |

---

## 7. 소스 코드

**GitHub Repository:** https://github.com/Duckcchun/DKU_LuckyDraw

---

## 8. AI 도구 사용 내역

개발 과정에서 Kiro(AI 어시스턴트)를 부분적으로 활용하였습니다.  
주로 코드 구조 잡을 때 참고용으로 사용했고, 세부 로직이나 디버깅은 직접 수행했습니다.

- 초기 프로젝트 구조 설계 참고
- Docker, Nginx 설정 파일 초안 작성 보조
- Railway 배포 시 에러 원인 분석 참고

---

## 9. 배포 환경 설정

### Railway 환경변수

| 변수명 | 설명 |
|--------|------|
| `DATABASE_URL` | PostgreSQL 연결 URL (Railway 자동 제공) |
| `DJANGO_SECRET_KEY` | Django 시크릿 키 |
| `DJANGO_DEBUG` | 디버그 모드 (False) |
| `DJANGO_ALLOWED_HOSTS` | 허용 호스트 (.railway.app) |
| `CSRF_TRUSTED_ORIGINS` | CSRF 허용 Origin |

### Docker 환경변수 (.env)

| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| `DB_NAME` | lottodb | 데이터베이스명 |
| `DB_USER` | lottouser | DB 사용자 |
| `DB_PASSWORD` | lottopass | DB 비밀번호 |
| `DB_HOST` | db | DB 호스트 (Docker 서비스명) |
| `DB_PORT` | 5432 | DB 포트 |

---

## 10. 향후 개선 사항

- [ ] 실제 금액 시스템 (가상 포인트) 도입
- [ ] 당첨 금액 계산 로직 추가
- [ ] 이메일 알림 기능
- [ ] REST API 제공 (DRF)
- [ ] 통계 차트 (Chart.js)
- [ ] SSL/HTTPS 적용
- [ ] CI/CD 파이프라인 구성

---

## 11. 참고 자료

- [Django 공식 문서](https://docs.djangoproject.com/)
- [Docker Compose 문서](https://docs.docker.com/compose/)
- [PostgreSQL 문서](https://www.postgresql.org/docs/)
- [Bootstrap 5 문서](https://getbootstrap.com/docs/5.3/)
- [Nginx 공식 문서](https://nginx.org/en/docs/)
- [Railway 배포 문서](https://docs.railway.app/)
- [WhiteNoise 문서](https://whitenoise.readthedocs.io/)
- [dj-database-url 문서](https://github.com/jazzband/dj-database-url)
