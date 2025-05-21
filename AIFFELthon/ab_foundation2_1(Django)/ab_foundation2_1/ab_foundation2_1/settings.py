from pathlib import Path
import os
import json

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-s8%1v#a1cp+6=^doo_s=1trnr-4y$9h1w%0@76ui#mmp^9=)!="

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [] # ★ 프로덕션 환경에서는 실제 도메인 및 IP 주소를 추가해야 합니다.

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Local apps
    "users",
    "accounting",
]

# INSTALLED_APPS += ["users", "accounting"] # 위에서 이미 추가됨

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    #"django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ab_foundation2_1.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # 이 줄 또는 아래 Path 객체 사용 줄 중 하나만 사용 권장
        # 'DIRS': [BASE_DIR / "templates"],           # Path 객체 사용 시
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"] # 위에서 이미 설정됨, 중복 제거 또는 일관성 유지
STATICFILES_DIRS = [BASE_DIR / "static"]

WSGI_APPLICATION = "ab_foundation2_1.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": 'ab_foundation2_1_db',
        'USER': 'ab_foundation2_1',
        'PASSWORD': 'ab_foundation@123',
        'HOST': 'localhost', # ★ 명시적으로 추가하는 것이 좋음 (기본값이지만)
        'PORT': '5432',      # ★ 명시적으로 추가하는 것이 좋음 (기본값이지만)
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "ko-kr" # ★ 한국어로 변경 고려
TIME_ZONE = "Asia/Seoul" # ★ 한국 시간으로 변경 고려

USE_I18N = True

USE_TZ = True # True로 유지하는 것이 좋음


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/" # 또는 "/static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 세션을 DB에 저장 (기본값이지만 명시해주는 게 좋음)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# --- iframe 관련 설정 추가 고려 ---
X_FRAME_OPTIONS = 'SAMEORIGIN' # ←★ 추가: 동일 출처의 iframe 내에서만 허용

# --- API 키 로드 함수 및 설정 (기존과 동일) ---
KEY_FILE = BASE_DIR / "secrets" / "api_keys.json"

def _load_api_keys(path: Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[WARNING] API‑key file not found → {path}")
    except json.JSONDecodeError:
        print(f"[WARNING] API‑key file JSON 오류 → {path}")
    return {}

_API_KEYS = _load_api_keys(KEY_FILE)

GEMINI_API_KEY = _API_KEYS.get("GEMINI_API_KEY", "")
OPENAI_API_KEY = _API_KEYS.get("OPENAI_API_KEY", "")

OUR_COMPANY_ENTITY_ID = 99 # 데이터베이스에 저장된 우리 회사 Entity의 ID
OUR_COMPANY_INFO = {
    "name": "AB Foundation GmbH",
    # 필요하다면 은행 정보 등 추가
    "bank": "우리은행",
    "bic_swift": "WOOR KR SE XXX",
    "bank_account_no": "1002-xxx-yyyyyy",
    # ... 기타 정보
}

# Booking Document Number 생성을 위한 고객 번호
# 실제 고객 번호 또는 식별자로 대체하세요.
CUSTOMER_NUMBER_FOR_BOOKING_DOC = "DE000001" # 예시 고객 번호

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {name} {message}', # 로거 이름(name) 추가
            'style': '{',
        },
        'django.server': { # django.server 로거를 위한 포맷터
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple', # 또는 'verbose'
        },
        'django.server': { # django.server 핸들러
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO', # 기본 로깅 레벨 (INFO 이상만)
    },
    'loggers': {
        'django': { # Django 내부 로거
            'handlers': ['console'],
            'level': 'INFO', # Django 내부 로그는 INFO 레벨로 (너무 많지 않게)
            'propagate': False,
        },
        'django.db.backends': { # ★★★ 데이터베이스 쿼리 로깅 ★★★
            'handlers': ['console'],
            'level': 'DEBUG', # SQL 쿼리를 보려면 DEBUG 레벨로 설정
            'propagate': False,
        },
        'accounting': { # 'accounting' 앱의 로거 (views.py 등에서 logger = logging.getLogger(__name__) 사용 시)
            'handlers': ['console'],
            'level': 'DEBUG', # 앱의 로그는 DEBUG 레벨까지 모두 출력
            'propagate': False,
        },
        'django.server': { # runserver 로그를 위한 로거
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

# views.py 상단에 로거 이름을 지정할 때
# logger = logging.getLogger(__name__) # 이 경우 로거 이름은 'views'가 됨

# 만약 위 LOGGING 설정의 'loggers' 부분을 사용한다면,
# views.py의 logger = logging.getLogger(__name__) 부분이 해당 로거 설정을 따릅니다.
# 'root' 로거 설정은 특정 로거에 설정이 없을 때 적용됩니다.


ATOMIC_REQUESTS = True