"""
Apps configuration for test module.
"""

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class TestConfig(AppConfig):
    label = "test"
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.test"
    verbose_name = "Test"

    def ready(self):
        """Called when the app is ready."""
        # Note: Periodic tasks are now handled by Celery Beat in core/celery.py
        # Test suite is scheduled automatically
        pass
