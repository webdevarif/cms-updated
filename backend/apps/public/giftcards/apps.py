"""
Apps configuration for gift cards module.
"""
from django.apps import AppConfig


class GiftCardsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.public.giftcards'
    verbose_name = 'Gift Cards'
    
    def ready(self):
        """Register signals and services"""
        # Register with core services
        self.register_core_services()
    
    def register_core_services(self):
        """Register gift cards with core services"""
        try:
            from core.services.registry import ServiceRegistry
            ServiceRegistry.register_service(
                'giftcards', 
                'GiftCardService', 
                'apps.public.giftcards.services.GiftCardService'
            )
        except ImportError:
            # Core services not available
            pass
