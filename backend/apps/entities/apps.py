"""
Apps configuration for entities app.
"""

from django.apps import AppConfig


class EntitiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.entities"
    verbose_name = "Entities"

    def ready(self):
        """
        Import signals module to register signal handlers.
        """
        import apps.entities.signals
