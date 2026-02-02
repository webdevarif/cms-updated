"""
Django app configuration for forms app."""

from django.apps import AppConfig


class FormsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.forms"
    verbose_name = "Forms"

    def ready(self):
        """Import signals when app is ready."""
        pass
