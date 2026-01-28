from django.apps import AppConfig


class ThemesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.themes"
    verbose_name = "Themes"

    def ready(self):
        """Import signals for automatic theme handling"""
        try:
            from . import signals
        except ImportError:
            # Signals module not available - theme functionality will be limited
            import logging

            logger = logging.getLogger(__name__)
            logger.warning("Theme signals module not found - some theme features may not work")
