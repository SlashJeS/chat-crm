from config.settings.env import get_optional_env

from .base import *  # noqa: F403

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

_csrf_origins = get_optional_env("CSRF_TRUSTED_ORIGINS")
if _csrf_origins:
    CSRF_TRUSTED_ORIGINS = [
        origin.strip()
        for origin in _csrf_origins.split(",")
        if origin.strip()
    ]
