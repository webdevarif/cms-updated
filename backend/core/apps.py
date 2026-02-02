"""
Core app configuration for scheduling recurring tasks.
"""

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    """Core app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Core"

    def ready(self):
        """Called when the app is ready."""
        # Note: Periodic tasks are now handled by Celery Beat in core/celery.py
        # Translation sync and test suite are scheduled automatically
        pass
