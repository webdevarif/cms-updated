"""
Pages app configuration.
"""

from django.apps import AppConfig


class PagesConfig(AppConfig):
    label = "pages"
    """Pages app configuration"""
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pages"
    verbose_name = "Pages"

    def ready(self):
        """Initialize app when ready"""
        pass
