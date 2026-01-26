"""
Gift cards app configuration.
"""
from django.apps import AppConfig


class GiftcardsConfig(AppConfig):
    """Gift cards app configuration"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.giftcards'
    verbose_name = 'Gift Cards'
    
    def ready(self):
        """Initialize app when ready"""
        pass
