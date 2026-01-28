"""
Development settings for Digital Farmers CMS.

These settings are specific to the development environment.
"""

from .base import *  # noqa

# Debug settings
DEBUG = True  # Enable debug mode for development (serves static files)

# Allow all hosts in development
ALLOWED_HOSTS = ["*"]

# Disable SSL redirect in development
SECURE_SSL_REDIRECT = False

# Database
DATABASES["default"]["TEST"] = {
    "NAME": f"test_{DATABASES['default']['NAME']}",
}

# Cache - Use Redis for development (consistent with production)
# django-ratelimit requires shared cache with atomic increment support
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# For development without Redis, use custom cache that supports atomic ops
try:
    import redis
    from redis.exceptions import ConnectionError

    # Test connection
    r = redis.Redis(host="127.0.0.1", port=6379, db=1)
    r.ping()
    # Redis is available - keep Redis configuration
except (ImportError, ConnectionError, Exception):
    # Use custom development cache that supports atomic operations
    CACHES["default"] = {
        "BACKEND": "core.cache_backends.DevelopmentCache",
    }

# Email backend
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Django Debug Toolbar
# INSTALLED_APPS += [
#     "debug_toolbar",
# ]

# MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

INTERNAL_IPS = [
    "127.0.0.1",
]

# Debug Toolbar configuration
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: True,
    "RENDER_PANELS": {
        "djdt.panels.SQLPanel": {
            "SQL_WARNING_THRESHOLD": 100,
        },
    },
}

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True

# Logging
LOGGING["loggers"] = {
    "django": {
        "handlers": ["console"],
        "level": "DEBUG",
        "propagate": True,
    },
    "core": {
        "handlers": ["console"],
        "level": "DEBUG",
        "propagate": True,
    },
}
