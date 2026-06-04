from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

from config.settings.env import (
    get_bool_env,
    get_env,
    get_int_env,
    get_list_env,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = BASE_DIR.parent

load_dotenv(REPO_ROOT / ".env")
if not Path("/.dockerenv").exists():
    load_dotenv(BASE_DIR / ".env", override=True)

SECRET_KEY = get_env("DJANGO_SECRET_KEY")
DEBUG = get_bool_env("DJANGO_DEBUG")
ALLOWED_HOSTS = get_list_env("DJANGO_ALLOWED_HOSTS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "channels",
    "apps.accounts",
    "apps.model_accounts",
    "apps.conversations",
    "apps.realtime",
    "apps.monitoring",
    "apps.presence",
    "apps.demo",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default=get_env("DATABASE_URL"),
        conn_max_age=600,
    )
}

REDIS_URL = get_env("REDIS_URL")

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                {
                    "address": REDIS_URL,
                    "socket_connect_timeout": 5,
                    "socket_timeout": None,
                }
            ],
        },
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = get_list_env("CORS_ALLOWED_ORIGINS")

RESPONSE_SLA_SECONDS = get_int_env("RESPONSE_SLA_SECONDS")
PRESENCE_HEARTBEAT_INTERVAL_SECONDS = get_int_env("PRESENCE_HEARTBEAT_INTERVAL_SECONDS")
PRESENCE_GRACE_SECONDS = get_int_env("PRESENCE_GRACE_SECONDS")
MONITOR_REFRESH_SECONDS = get_int_env("MONITOR_REFRESH_SECONDS")
FRONTEND_BASE_URL = get_env("FRONTEND_BASE_URL")

DEMO_ACTIVITY_ENABLED = get_bool_env("DEMO_ACTIVITY_ENABLED")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
