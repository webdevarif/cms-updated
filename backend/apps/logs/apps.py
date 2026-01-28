"""
Apps configuration for logs app.
"""
from django.apps import AppConfig


class LogsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.logs"
    verbose_name = "Logs"

    def ready(self):
        """Register services"""
        # Register with core services
        self.register_core_services()

    def register_core_services(self):
        """Register logs with core services"""
        try:
            from core.services.registry import ServiceRegistry

            ServiceRegistry.register_service("logs", "LogService", "apps.logs.services.LogService")
        except ImportError:
            # Core services not available
            pass
