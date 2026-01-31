"""
Django settings for testing environment.
Uses SQLite for faster test execution.
"""

from .base import *

DEBUG = True
SECRET_KEY = 'test-secret-key-not-for-production'

# Use SQLite for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Faster password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable throttling in tests
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {}

# Use console email backend
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable Celery tasks in tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
        'level': 'DEBUG',
    },
}

# CORS - allow all for testing
CORS_ALLOW_ALL_ORIGINS = True
