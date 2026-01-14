# HISUBTORY Backend (Django)

지하철 역 기반 역사 숏스토리(웹툰) 서비스 **HISUBTORY**의 백엔드 레포지토리입니다.  
서비스 기능보다 **AWS 인프라 설계 + 배포 자동화 + 운영 안정성**을 중심으로 구성했습니다.

---

## 🧭 Overview

- **Backend**: Django REST API + Gunicorn
- **DB**: Amazon RDS (MySQL)
- **Session/Cache**: Amazon ElastiCache (Redis, **TLS 적용**)
- **Static/Image**: S3 업로드 + CloudFront 서빙 (이미지/정적 분리)
- **CI/CD**: GitHub Actions → AWS CodeDeploy → EC2 자동 배포

---

### 🧾 Service at a glance
- 지하철 **역을 선택**하면 해당 역의 역사/스토리를 **짧은 웹툰(에피소드/컷)** 형태로 제공
- 백엔드는 **JSON API**로 콘텐츠 메타데이터/캡션/유저 활동(열람 기록)을 제공
- 이미지는 **CloudFront(S3)** 로 분리 서빙해 빠르게 로딩

---

## 🏗 Architecture (High-level)

### Request Flow
1. User → (ALB) → **Front EC2 (Nginx + React build)**
2. Front `/api/*` → **Backend EC2 (Gunicorn + Django)**
3. Backend ↔ **RDS(MySQL)** (메타/캡션/유저 기록)
4. Backend ↔ **ElastiCache Redis** (세션/캐시)
5. Images/Static: Client → **CloudFront** → **S3**

> API는 **JSON만 제공**하고, 이미지/정적 파일은 **CloudFront(S3 origin)** 로 분리 서빙합니다.

---

## ✅ Key Features (Backend)

- 역/웹툰/에피소드/컷 데이터 조회 API
- 유저 활동(열람 기록 등) 저장/조회
- **Redis 기반 세션 유지** (EC2 재시작/재배포 시에도 로그인 유지)

---

## 🧩 Core Data Model (Summary)

- `subway_line` / `subway_station` : 지하철 노선/역
- `webtoons` : 역/노선 기반 콘텐츠 단위
- `episodes` : 웹툰의 에피소드
- `cuts` : 에피소드 내 컷 이미지/캡션(CloudFront URL과 매핑)
- (옵션) `user_viewed_episode`, `bookmark` 등 유저 활동 테이블

---

## 🔐 Redis (ElastiCache) Session/Cache

### Django Settings (example)
- Cache backend: `django_redis.cache.RedisCache`
- Session engine: `django.contrib.sessions.backends.cache`
- **TLS 연결**: `rediss://` 또는 TLS 옵션 적용

> ElastiCache는 TLS가 활성화되어 있어 `redis-cli --tls ...` 로 접속합니다.

---

## 🚀 CI/CD (GitHub Actions → CodeDeploy)

### Pipeline
- Push (main/dev) →
- GitHub Actions: package(artifact zip) →
- CodeDeploy: appspec/hooks 기반으로 EC2 배포 →
- Gunicorn 재시작으로 반영

### Included in Artifact
- `appspec.yml`
- `scripts/` (hooks)
- Django source code

---

## ⚙️ Local Setup

### 1) Requirements
- Python 3.x
- (Optional) Redis, MySQL (로컬 환경에 맞게)

### 2) Install
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
## 3) Environment Variables

`.env` 예시(로컬/서버 환경에 맞게 변경):

> ⚠️ 보안 주의: `.env`는 커밋하지 마세요. (`.gitignore`에 추가)

### (1) Django 기본 설정

```env
# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,hisub-alb-xxxx.ap-northeast-2.elb.amazonaws.com

# (선택) CORS/CSRF
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://your-front-domain
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://your-front-domain
```

### (2) Database (RDS MySQL)
```env
DB_HOST=your-rds-endpoint.ap-northeast-2.rds.amazonaws.com
DB_PORT=3306
DB_NAME=hisubtory_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

### (3) Redis (ElastiCache for Redis)

ElastiCache Redis 엔드포인트를 Django에서 **캐시/세션 저장소**로 쓰기 위한 환경변수 예시입니다.  
(우리 프로젝트처럼 TLS로 붙는 경우 `redis-cli --tls ...`가 필요하므로, Django 설정에서도 TLS 고려가 필요합니다.)

#### ✅ 권장 .env 예시 (TLS 고려)

```env
# Redis Endpoint (ElastiCache)
REDIS_HOST=clustercfg.hisub-redis.xxxxx.apn2.cache.amazonaws.com
REDIS_PORT=6379
REDIS_DB=1

# 프로젝트에서 조합해서 쓰는 형태라면 (settings.py에서 REDIS_URL 생성)
REDIS_URL=rediss://clustercfg.hisub-redis.xxxxx.apn2.cache.amazonaws.com:6379/1

# (선택) TLS 사용 여부를 플래그로 두는 경우
REDIS_USE_TLS=True
```
#### 🔎 설명

- `REDIS_HOST`: ElastiCache 엔드포인트(일반적으로 `clustercfg...apn2.cache.amazonaws.com` 형태)
- `REDIS_PORT`: Redis 포트(기본값 `6379`)
- `REDIS_DB`: Redis DB 인덱스(0~15). 세션/캐시용으로 분리하려면 `1`처럼 0이 아닌 값 추천
- `REDIS_URL`: Django에서 한 줄로 쓰기 좋은 연결 문자열  
  - TLS 미사용: `redis://<host>:<port>/<db>`  
  - TLS 사용: `rediss://<host>:<port>/<db>`
- `REDIS_USE_TLS`: 프로젝트에서 TLS 여부를 조건 분기할 때 쓰는 플래그(선택)

---

### (4) AWS (S3 / CloudFront)

S3에 이미지를 올리고, CloudFront 도메인으로 서빙할 때 필요한 환경변수 예시입니다.

```env
AWS_REGION=ap-northeast-2
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

S3_BUCKET_NAME=hisubtory-bucket
CLOUDFRONT_DOMAIN=d27nsin45nib0r.cloudfront.net
```
#### 🔎 설명
- AWS_REGION: 리전 (예: ap-northeast-2)
- AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY: IAM Access Key (서버/CI에서 S3 접근용)
- S3_BUCKET_NAME: 이미지 업로드 버킷 이름
- CLOUDFRONT_DOMAIN: 이미지 URL 생성에 사용하는 CDN 도메인
예) https://d27nsin45nib0r.cloudfront.net/media/.../cut_1.png

---

### (5) 기타 (선택)

운영/배포 환경에서 로그나 실행 옵션을 분리하고 싶을 때 사용하는 값들입니다.

```env
LOG_LEVEL=INFO
DJANGO_SETTINGS_MODULE=project.settings
DJANGO_ALLOWED_HOSTS=hisub-alb-xxxx.ap-northeast-2.elb.amazonaws.com,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://hisub-alb-xxxx.ap-northeast-2.elb.amazonaws.com
```
#### 🔎 설명

- `LOG_LEVEL`: 서버 로그 출력 수준  
  - 예: `DEBUG`(개발), `INFO`(운영), `WARNING/ERROR`(최소 로그)
- `DJANGO_SETTINGS_MODULE`: Django 설정 모듈 지정(기본값이면 생략 가능)
- `DJANGO_ALLOWED_HOSTS`: Django가 요청을 허용할 호스트 목록  
  - ALB 도메인, 서버 도메인, `localhost` 등을 콤마(`,`)로 구분해서 등록
- `CORS_ALLOWED_ORIGINS`: 프론트 도메인에서 API 호출을 허용하기 위한 CORS 설정  
  - 프론트가 별도 도메인/서브도메인이면 등록 권장

> 참고: `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`는 `.env`로 두고 `settings.py`에서 `split(",")`로 파싱하면 관리가 편합니다.

---

### (6) Run (Local)
``` bash
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```
