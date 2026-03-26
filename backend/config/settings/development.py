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

# Relaxed throttling in development - keep scopes but remove limits
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # noqa: F405
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {
        'anon_burst': '9999/min',
        'anon_sustained': '99999/hour',
        'user_burst': '9999/min',
        'user_sustained': '99999/hour',
        'auth': '9999/min',
        'ai_agent': '9999/hour',
    },
}
