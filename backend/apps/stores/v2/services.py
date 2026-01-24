"""
Store service for business logic.
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone
from apps.logs.models import LogEntry
from apps.logs.tasks import log_event_async


class StoreService:
    """Store business logic following DFCMS patterns"""
    
    @staticmethod
    @transaction.atomic
    def create_store(owner, store_data):
        """Create a new store with settings using centralized service"""
        from .models import Store, StoreSettings
        from apps.logs.tasks import log_event_async
        
        # Create store using centralized method
        store = Store.objects.create(
            owner=owner,
            name=store_data['name'],
            slug=store_data.get('slug', ''),
            description=store_data.get('description', ''),
            store_type=store_data.get('store_type', 'ecommerce')
        )
        
        # Create default settings using centralized method
        StoreService.create_default_settings(store, owner)
        
        log_event_async.delay({
            'event_type': 'STORE_CREATED',
            'message': f"Store created: {store.name}",
            'store': store,
            'user': owner,
            'entity_type': 'Store',
            'entity_id': store.id,
            'metadata': {
                'store_name': store.name,
                'store_slug': store.slug
            }
        })
        
        return store
    
    @staticmethod
    def create_default_settings(store, owner):
        """Create default store settings"""
        from .models import StoreSettings
        
        return StoreSettings.objects.create(
            store=store,
            site_name=store.name,
            contact_email=owner.email
        )
    
    @staticmethod
    def update_store(store, update_data, user=None):
        """Update store with logging"""
        try:
            old_data = {
                'name': store.name,
                'status': store.status,
                'description': store.description
            }
            
            for field, value in update_data.items():
                if hasattr(store, field):
                    setattr(store, field, value)
            
            store.save()
            
            # Log update
            log_event_async.delay({
                'event_type': 'CONTENT_UPDATE',
                'message': f"Store updated: {store.name}",
                'user': user,
                'store': store,
                'entity_type': 'Store',
                'entity_id': store.id,
                'metadata': {
                    'old_data': old_data,
                    'new_data': update_data
                }
            })
            
            return store
            
        except Exception as e:
            log_event_async.delay({
                'event_type': 'SYSTEM_ERROR',
                'message': f"Failed to update store: {str(e)}",
                'user': user,
                'store': store,
                'level': 'ERROR',
                'metadata': {'error': str(e), 'update_data': update_data}
            })
            raise
    
    @staticmethod
    def verify_store(store, token):
        """Verify store email"""
        if store.verification_token == token:
            store.status = 'active'
            store.verification_token = None
            store.save()
            
            log_event_async.delay({
                'event_type': 'CONTENT_UPDATE',
                'message': f"Store verified: {store.name}",
                'store': store,
                'entity_type': 'Store',
                'entity_id': store.id,
                'metadata': {'verification': True}
            })
            
            return True
        return False
    
    @staticmethod
    def get_store_analytics(store, days=30):
        """Get store analytics data from logs"""
        since = timezone.now() - timedelta(days=days)
        
        # Get analytics from logs app
        page_views = LogEntry.objects.filter(
            store=store,
            event_type='PAGE_VIEW',
            created_at__gte=since
        ).count()
        
        unique_visitors = LogEntry.objects.filter(
            store=store,
            event_type='PAGE_VIEW',
            created_at__gte=since
        ).values('session_id').distinct().count()
        
        security_events = LogEntry.objects.filter(
            store=store,
            is_suspicious=True,
            created_at__gte=since
        ).count()
        
        return {
            'page_views': page_views,
            'unique_visitors': unique_visitors,
            'security_events': security_events,
            'period_days': days,
        }
