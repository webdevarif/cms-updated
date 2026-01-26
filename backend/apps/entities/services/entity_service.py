"""
Services for entities app.
"""
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
import logging
from apps.logs.tasks import log_event_async

logger = logging.getLogger(__name__)


class EntityService:
    """Shared entity interaction service"""
    
    @staticmethod
    @transaction.atomic
    def toggle_action(user, content_object, action_slug, store=None):
        """Toggle an action (like/unlike, favorite/unfavorite)"""
        from ..models import EntityAction, EntityInteraction
        
        # Validate store is provided
        if not store:
            raise ValidationError("Store context is required for entity actions")
        
        # Get action with store validation
        try:
            action = EntityAction.objects.get(store=store, slug=action_slug)
        except EntityAction.DoesNotExist:
            raise ValidationError(f"Action '{action_slug}' not found for this store")
        
        if action.action_type != 'toggle':
            raise ValueError(f"Action '{action.name}' is not a toggle action")
        
        # Get content type
        content_type = ContentType.objects.get_for_model(content_object)
        
        # Check existing interaction
        try:
            interaction = EntityInteraction.objects.get(
                store=store,
                action=action,
                user=user,
                content_type=content_type,
                object_id=content_object.id
            )
            
            # Remove existing interaction
            interaction.delete()
            action_performed = 'removed'
            
        except EntityInteraction.DoesNotExist:
            # Create new interaction
            interaction = EntityInteraction.objects.create(
                store=store,
                action=action,
                user=user,
                content_type=content_type,
                object_id=content_object.id
            )
            action_performed = 'added'
        
        # Log action
        log_event_async.delay({
            'event_type': f'ENTITY_{action_performed.upper()}',
            'message': f"Entity action {action_performed}: {action.name}",
            'user': user,
            'store': store,
            'entity_type': 'entity_interaction',
            'entity_id': interaction.id if action_performed == 'added' else None,
            'metadata': {
                'action_slug': action_slug,
                'content_type': content_type.model,
                'object_id': content_object.id
            }
        })
        
        return {
            'action': action_performed,
            'entity_action': action,
            'interaction': interaction if action_performed == 'added' else None
        }
    
    @staticmethod
    def get_interaction_count(content_object, action_slug, store=None):
        """Get total count for an action"""
        from ..models import EntityAction, EntityInteraction
        
        # Validate store is provided
        if not store:
            raise ValidationError("Store context is required for entity actions")
        
        try:
            action = EntityAction.objects.get(store=store, slug=action_slug)
        except EntityAction.DoesNotExist:
            raise ValidationError(f"Action '{action_slug}' not found for this store")
        
        content_type = ContentType.objects.get_for_model(content_object)
        
        return EntityInteraction.objects.filter(
            store=store,
            action=action,
            content_type=content_type,
            object_id=content_object.id,
            is_active=True
        ).count()
    
    @staticmethod
    def get_user_interactions(user, content_object, store=None):
        """Get all user interactions for an object"""
        from ..models import EntityInteraction
        
        # Validate store is provided
        if not store:
            raise ValidationError("Store context is required for entity actions")
        
        content_type = ContentType.objects.get_for_model(content_object)
        
        return EntityInteraction.objects.filter(
            store=store,
            user=user,
            content_type=content_type,
            object_id=content_object.id,
            is_active=True
        ).select_related('action')
    
    @staticmethod
    def get_popular_objects(action_slug, limit=10, store=None):
        """Get most popular objects for an action"""
        from ..models import EntityAction, EntityInteraction
        from django.db.models import Count
        
        action = EntityAction.objects.get(store=store, slug=action_slug)
        
        return EntityInteraction.objects.filter(
            store=store,
            action=action,
            is_active=True
        ).values('content_type', 'object_id').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]
