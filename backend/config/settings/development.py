"""
Development settings.
Usage: DJANGO_SETTINGS_MODULE=config.settings.development
"""

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ['*']

# Use SQLite for quick local dev without PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Console email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS - allow all in dev
CORS_ALLOW_ALL_ORIGINS = True
