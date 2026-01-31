"""
Production settings.
Usage: DJANGO_SETTINGS_MODULE=config.settings.production
"""

from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')  # noqa: F405

# ---------- Security ----------
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ---------- CSP ----------
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_CONNECT_SRC = ("'self'", os.environ.get('FRONTEND_URL', 'https://localhost:3000'))  # noqa: F405

# ---------- CORS (production) ----------
CORS_ALLOWED_ORIGINS = os.environ.get(  # noqa: F405
    'CORS_ALLOWED_ORIGINS',
    'https://localhost:3000'
).split(',')

CORS_ALLOW_CREDENTIALS = True

# ---------- Static files ----------
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')  # noqa: F405

# ---------- Database (production) ----------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'clinic_platform'),  # noqa: F405
        'USER': os.environ.get('DB_USER', 'postgres'),  # noqa: F405
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),  # noqa: F405
        'HOST': os.environ.get('DB_HOST', 'db'),  # noqa: F405
        'PORT': os.environ.get('DB_PORT', '5432'),  # noqa: F405
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 5,
        },
    }
}

# ---------- Cache (Redis) ----------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://redis:6379/1'),  # noqa: F405
    }
}

# ---------- Rate Limiting ----------
RATELIMIT_USE_CACHE = 'default'

# ---------- Logging ----------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.environ.get('LOG_FILE', '/var/log/clinic/django.log'),  # noqa: F405
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ---------- Email (production) ----------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')  # noqa: F405
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))  # noqa: F405
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')  # noqa: F405
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')  # noqa: F405
