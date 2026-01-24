"""Theme service."""
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class ThemeService:
    """Theme management service"""
    
    @staticmethod
    @transaction.atomic
    def create_theme(store, name, user=None):
        """Create a new theme with default components using centralized service"""
        from ..models import Theme, ColorScheme, Typography
        from apps.logs.tasks import log_event_async
        
        # Create theme using centralized method
        theme = ThemeService.create_theme_base(store, name, user)
        
        # Create default color scheme
        ThemeService.create_default_color_scheme(theme, store)
        
        # Create typography
        ThemeService.create_default_typography(theme, store)
        
        log_event_async.delay({
            'event_type': 'THEME_CREATED',
            'message': f"Theme created: {theme.name}",
            'store': store,
            'user': user,
            'entity_type': 'Theme',
            'entity_id': theme.id,
            'metadata': {
                'theme_name': theme.name,
                'theme_id': theme.id
            }
        })
        
        return theme
    
    @staticmethod
    def create_theme_base(store, name, user=None):
        """Create base theme"""
        from ..models import Theme
        
        return Theme.objects.create(
            store=store,
            name=name,
            is_active=False,
            created_by=user
        )
    
    @staticmethod
    def create_default_color_scheme(theme, store):
        """Create default color scheme"""
        from ..models import ColorScheme
        
        return ColorScheme.objects.create(
            theme=theme,
            store=store,
            name="Default",
            primary_color="#000000",
            secondary_color="#666666",
            accent_color="#007bff",
            background_color="#ffffff",
            text_color="#333333"
        )
    
    @staticmethod
    def create_default_typography(theme, store):
        """Create default typography"""
        from ..models import Typography
        
        return Typography.objects.create(
            theme=theme,
            store=store,
            font_family="Arial",
            font_size="16px",
            line_height="1.5"
        )
    
    @staticmethod
    def get_active_theme(store):
        """Get active theme for a store"""
        from core.services.theme import ThemeService
        
        return ThemeService.get_active_theme(store)
    
    @staticmethod
    def activate_theme(theme_id):
        """Activate a theme"""
        from ..models import Theme
        from core.services.theme import ThemeService
        
        theme = ThemeService.get_theme(theme_id)
        theme.activate()
        return theme
