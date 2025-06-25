from .base import *
import tempfile

DEBUG = False

ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "test_rm_platform",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": "5432",
        "OPTIONS": {
            # 'MAX_CONNS': 5,  # Removed invalid option
        },
        "TEST": {
            "NAME": "test_rm_platform",
        },
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    "redis": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.testserver.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "test_email@testserver.com"
EMAIL_HOST_PASSWORD = "test_password"

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

MEDIA_ROOT = tempfile.mkdtemp()

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["console"],
    },
}

AXES_ENABLED = False

REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {
    "anon": "1000/hour",
    "user": "10000/hour",
    "login": "50/min",
    "register": "30/min",
}

SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(minutes=60)
SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] = timedelta(days=1)

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

MIGRATION_MODULES = {
    "auth": None,
    "contenttypes": None,
    "sessions": None,
    "messages": None,
    "staticfiles": None,
    "guardian": None,
    "axes": None,
    "django_otp": None,
    "token_blacklist": None,
}

SPECTACULAR_SETTINGS["SERVE_INCLUDE_SCHEMA"] = False
