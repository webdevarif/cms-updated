"""
Apps configuration for test module.
"""
from django.apps import AppConfig


class TestConfig(AppConfig):
    label = "test"
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.test"
    verbose_name = "Test"
