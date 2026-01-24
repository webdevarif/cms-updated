"""
Development settings for Digital Farmers CMS.

These settings are specific to the development environment.
"""

from .base import *  # noqa

# Debug settings
DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Database
DATABASES['default']['TEST'] = {
    'NAME': f"test_{DATABASES['default']['NAME']}",
}

# Email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Django Debug Toolbar
INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

INTERNAL_IPS = [
    '127.0.0.1',
]

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True

# Logging
LOGGING['loggers'] = {
    'django': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': True,
    },
    'core': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': True,
    },
}
