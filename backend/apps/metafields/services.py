"""
Metafields service module for metafield operations.
"""
from apps.metafields.models import Metafield, MetafieldDefinition
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction


class MetafieldService:
    """Core service for metafield operations"""

    @staticmethod
    def get_metafield_definition(store, namespace, key):
        """Get a metafield definition by namespace and key"""
        return MetafieldDefinition.objects.get(store=store, namespace=namespace, key=key)

    @staticmethod
    def get_metafield(instance, definition):
        """Get a metafield value for an instance"""
        content_type = ContentType.objects.get_for_model(instance)
        return Metafield.objects.filter(
            definition=definition,
            content_type=content_type,
            object_id=instance.id,
            store=instance.store,
        ).first()

    @staticmethod
    def set_metafield(instance, namespace, key, value):
        """Set a metafield value for an instance"""
        # Get or create definition
        definition, created = MetafieldDefinition.objects.get_or_create(
            store=instance.store,
            namespace=namespace,
            key=key,
            defaults={
                "name": f"{namespace}.{key}",
                "type": MetafieldService._infer_type(value),
                "content_types": [ContentType.objects.get_for_model(instance).model],
            },
        )

        # Get or create metafield
        content_type = ContentType.objects.get_for_model(instance)
        metafield, created = Metafield.objects.get_or_create(
            definition=definition,
            content_type=content_type,
            object_id=instance.id,
            store=instance.store,
        )

        # Set and save value
        metafield.set_value(value)
        metafield.save()

        return metafield

    @staticmethod
    def _infer_type(value):
        """Infer metafield type from Python type"""
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, (int, float)):
            return "number"
        elif isinstance(value, dict):
            return "json"
        return "text"

    @staticmethod
    def get_metafields_for_object(instance, namespace=None):
        """Get all metafields for an object, optionally filtered by namespace"""
        content_type = ContentType.objects.get_for_model(instance)
        queryset = Metafield.objects.filter(
            store=instance.store, content_type=content_type, object_id=instance.id
        ).select_related("definition")

        if namespace:
            queryset = queryset.filter(definition__namespace=namespace)

        return queryset

    @staticmethod
    def invalidate_metafield_cache(store):
        """Invalidate metafield cache for a store."""
        # Placeholder: implement actual cache invalidation logic
        pass

    @staticmethod
    def invalidate_definition_cache(store):
        """Invalidate metafield definition cache for a store."""
        # Placeholder: implement actual cache invalidation logic
        pass
