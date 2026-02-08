from django.apps import AppConfig


class ThemesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.themes"
    verbose_name = "Themes"

    def ready(self):
        """
        Import signals when the app is ready.
        """
        try:
            from . import signals  # noqa: F401
        except ImportError:
            # signals.py doesn't exist yet, that's fine
            pass
