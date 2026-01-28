"""
Testing settings for Digital Farmers CMS.

These settings are specific to the testing environment.
"""

from .base import *  # noqa

# Remove debug toolbar in tests
if "INSTALLED_APPS" in locals():
    INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]

# Use in-memory SQLite database for faster tests
if "DATABASES" in locals():
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable logging during tests
LOGGING = {}

# Disable password validation in tests
AUTH_PASSWORD_VALIDATORS = []

# Use faster password hasher for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable cache during tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
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
