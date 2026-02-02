"""
Test settings for Digital Farmers CMS.

These settings are optimized for reliable testing on Windows.
"""

import os
import tempfile

# =============================================================================
# DATABASE CONFIGURATION FOR TESTS
# =============================================================================
# Use a temporary file-based SQLite database for reliable testing on Windows
# This avoids the in-memory database issues while keeping tests fast
import uuid

from .base import *  # noqa

temp_db = os.path.join(tempfile.gettempdir(), f"cms_test_{uuid.uuid4().hex[:8]}.sqlite3")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": temp_db,
        "TEST": {
            "NAME": temp_db,
            "CREATE_DB": True,
        },
    }
}

# =============================================================================
# TEST OPTIMIZATIONS
# =============================================================================

# Remove debug toolbar and django-ratelimit in tests
INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in ["debug_toolbar", "django_ratelimit"]]

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable logging during tests
LOGGING = {}

# Disable password validation in tests
AUTH_PASSWORD_VALIDATORS = []

# Use a file-based cache to avoid django-ratelimit errors
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": os.path.join(tempfile.gettempdir(), "django_cache_test"),
    }
}

# Disable throttling during tests
if "REST_FRAMEWORK" in locals():
    REST_FRAMEWORK = {
        **REST_FRAMEWORK,
        "DEFAULT_THROTTLE_CLASSES": [],
    }

# Disable email sending during tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Disable CORS during tests
CORS_ALLOW_ALL_ORIGINS = True

# Test runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# Disable migrations for faster tests (optional)
# class DisableMigrations:
#     def __contains__(self, item):
#         return True
#
# MIGRATION_MODULES = DisableMigrations()
