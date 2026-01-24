"""
Apps configuration for test module.
"""
from django.apps import AppConfig


class TestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.test'
    verbose_name = 'Test'
