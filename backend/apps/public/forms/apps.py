"""
Apps configuration for forms module.
"""
from django.apps import AppConfig


class FormsConfig(AppConfig):
    """Forms app configuration"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.public.forms'
    verbose_name = 'Forms'
    
    def ready(self):
        """Register signals"""
        # Import models here to avoid circular imports
        from .models.forms import FormTemplate
        from .signals import form_created_signal
        from django.db.models.signals import post_save
        post_save.connect(form_created_signal, sender=FormTemplate)
        
        # Register with core services
        self.register_core_services()
    
    def register_core_services(self):
        """Register forms with core services"""
        try:
            from core.services.registry import ServiceRegistry
            ServiceRegistry.register_service('forms', 'FormService', 'apps.public.forms.v2.services.FormService')
        except ImportError:
            # Core services not available
            pass
