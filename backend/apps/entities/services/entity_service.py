"""
Services for entities app.
"""

import logging

from apps.analytics.services.event_service import EventService
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction

logger = logging.getLogger(__name__)


class EntityService:
    """Shared entity interaction service"""

    # Helper methods
    @staticmethod
    def _validate_store_context(store):
        """Validate that store context is provided"""
        if not store:
            raise ValidationError("Store context is required for entity actions")

    @staticmethod
    def _get_action(store, action_slug):
        """Get entity action with validation"""
        from ..models import EntityAction

        try:
            return EntityAction.objects.get(store=store, slug=action_slug)
        except EntityAction.DoesNotExist:
            raise ValidationError(f"Action '{action_slug}' not found for this store")

    @staticmethod
    def _get_content_type(content_object):
        """Get content type for object"""
        return ContentType.objects.get_for_model(content_object)

    @staticmethod
    def _get_or_create_interaction(store, action, user, content_type, content_object):
        """Get or create entity interaction"""
        from ..models import EntityInteraction

        try:
            # Check existing interaction
            interaction = EntityInteraction.objects.get(
                store=store,
                action=action,
                user=user,
                content_type=content_type,
                object_id=content_object.id,
            )
            return interaction, False
        except EntityInteraction.DoesNotExist:
            # Create new interaction
            interaction = EntityInteraction.objects.create(
                store=store,
                action=action,
                user=user,
                content_type=content_type,
                object_id=content_object.id,
            )
            return interaction, True

    # Toggle actions (like/unlike, favorite/unfavorite)
    @staticmethod
    @transaction.atomic
    def toggle_action(user, content_object, action_slug, store=None):
        """Toggle an action (like/unlike, favorite/unfavorite)"""
        EntityService._validate_store_context(store)

        action = EntityService._get_action(store, action_slug)

        if action.action_type != "toggle":
            raise ValueError(f"Action '{action.name}' is not a toggle action")

        content_type = EntityService._get_content_type(content_object)
        interaction, created = EntityService._get_or_create_interaction(
            store, action, user, content_type, content_object
        )

        action_performed = "added" if created else "removed"

        if not created:
            # Remove existing interaction
            interaction.delete()
            action_performed = "removed"

        # Log action
        EventService.log_event(
            event_type=f"ENTITY_{action_performed.upper()}",
            event_name=f"Entity action {action_performed}: {action.name}",
            properties={
                "user": user.id if user else None,
                "store": store.id if store else None,
                "entity_type": "entity_interaction",
                "entity_id": interaction.id if action_performed == "added" else None,
                "action_slug": action_slug,
                "content_type": content_type.model,
                "object_id": content_object.id,
            },
            user=user,
            store=store,
        )

        return {
            "action": action_performed,
            "entity_action": action,
            "interaction": interaction if action_performed == "added" else None,
        }

    # Rating actions (1-5 stars)
    @staticmethod
    def rate_action(user, content_object, action_slug, rating, store=None):
        """Rate an entity (1-5 stars)"""
        EntityService._validate_store_context(store)

        action = EntityService._get_action(store, action_slug)

        if action.action_type != "rating":
            raise ValueError(f"Action '{action.name}' is not a rating action")

        content_type = EntityService._get_content_type(content_object)

        # Create or update rating
        interaction, created = EntityService._get_or_create_interaction(
            store, action, user, content_type, content_object
        )

        interaction.rating = rating
        interaction.save()

        # Log rating
        EventService.log_event(
            event_type="ENTITY_RATED",
            event_name=f"Entity rated: {action.name} - {rating}",
            properties={
                "user": user.id if user else None,
                "store": store.id if store else None,
                "entity_type": "entity_rating",
                "entity_id": rating.id,
                "action_slug": action_slug,
                "content_type": content_type.model,
                "object_id": content_object.id,
                "rating": rating,
            },
            user=user,
            store=store,
        )

        return {
            "action": "rated",
            "entity_action": action,
            "interaction": interaction,
        }

    # Counter actions (view count, etc.)
    @staticmethod
    def counter_action(content_object, action_slug, store=None, user=None, increment=1):
        """Increment a counter action (view count, etc.)"""
        EntityService._validate_store_context(store)

        action = EntityService._get_action(store, action_slug)

        if action.action_type != "counter":
            raise ValueError(f"Action '{action.name}' is not a counter action")

        content_type = EntityService._get_content_type(content_object)

        # For counter actions, we typically don't need user tracking
        # This could be extended to track unique views per user if needed
        from ..models import EntityInteraction

        # Simple increment - could be enhanced for unique tracking
        interaction = EntityInteraction.objects.create(
            store=store,
            action=action,
            user=user,
            content_type=content_type,
            object_id=content_object.id,
            value={"increment": increment},
        )

        return {
            "action": "counted",
            "entity_action": action,
            "interaction": interaction,
        }

    # Single actions (upvote only, etc.)
    @staticmethod
    def single_action(user, content_object, action_slug, store=None):
        """Perform a single action (upvote only, etc.)"""
        EntityService._validate_store_context(store)

        action = EntityService._get_action(store, action_slug)

        if action.action_type != "single":
            raise ValueError(f"Action '{action.name}' is not a single action")

        content_type = EntityService._get_content_type(content_object)

        # Check if already performed
        from ..models import EntityInteraction

        existing = EntityInteraction.objects.filter(
            store=store,
            action=action,
            user=user,
            content_type=content_type,
            object_id=content_object.id,
            is_active=True,
        ).first()

        if existing:
            raise ValueError(f"Action '{action.name}' has already been performed")

        # Create new interaction
        interaction = EntityInteraction.objects.create(
            store=store,
            action=action,
            user=user,
            content_type=content_type,
            object_id=content_object.id,
        )

        # Log action
        EventService.log_event(
            event_type="ENTITY_SINGLE_ACTION",
            event_name=f"Single action performed: {action.name}",
            properties={
                "user": user.id if user else None,
                "store": store.id if store else None,
                "entity_type": "entity_action",
                "entity_id": action.id,
                "action_slug": action_slug,
                "content_type": content_type.model,
                "object_id": content_object.id,
            },
            user=user,
            store=store,
        )

        return {
            "action": "performed",
            "entity_action": action,
            "interaction": interaction,
        }

    # Query helpers
    @staticmethod
    def get_interaction_count(content_object, action_slug, store=None):
        """Get total count for an action"""
        EntityService._validate_store_context(store)

        action = EntityService._get_action(store, action_slug)
        content_type = EntityService._get_content_type(content_object)

        from ..models import EntityInteraction

        return EntityInteraction.objects.filter(
            store=store,
            action=action,
            content_type=content_type,
            object_id=content_object.id,
            is_active=True,
        ).count()

    @staticmethod
    def get_user_interactions(user, content_object, store=None):
        """Get all user interactions for an object"""
        EntityService._validate_store_context(store)

        content_type = EntityService._get_content_type(content_object)

        from ..models import EntityInteraction

        return EntityInteraction.objects.filter(
            store=store,
            user=user,
            content_type=content_type,
            object_id=content_object.id,
            is_active=True,
        ).select_related("action")

    @staticmethod
    def get_popular_objects(action_slug, limit=10, store=None):
        """Get most popular objects for an action"""
        from django.db.models import Count

        from ..models import EntityAction, EntityInteraction

        action = EntityService._get_action(store, action_slug)

        return (
            EntityInteraction.objects.filter(store=store, action=action, is_active=True)
            .values("content_type", "object_id")
            .annotate(count=Count("id"))
            .order_by("-count")[:limit]
        )
