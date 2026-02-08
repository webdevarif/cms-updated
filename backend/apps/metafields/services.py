"""
Metafields service module for metafield operations.
"""

from apps.metafields.models import Metafield, MetafieldDefinition

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction


class MetafieldService:
    """
    Canonical service for metafield operations.

    Provides read/write access to metafields by namespace/key for any resource,
    enforces types based on MetafieldDefinition, and offers convenient helpers
    for bulk operations. This is the primary abstraction for all metafield access.

    Responsibilities:
    - Read/write metafields by namespace/key for any resource
    - Enforce types based on MetafieldDefinition
    - Provide convenient helpers for bulk reads
    - Handle type inference and validation
    """

    # Internal type handling map for organizing current logic and future extensibility
    # This is the place to plug in new types later (similar to Shopify metafield types)
    TYPE_HANDLERS = {
        "text": "value_text",
        "number": "value_number",
        "boolean": "value_boolean",
        "date": "value_date",
        "url": "value_text",
        "json": "value_json",
        "select": "value_text",
        "multiselect": "value_text",
        "image": "value_media",
        "file": "value_media",
    }

    @staticmethod
    def get_metafield(instance, namespace, key, default=None):
        """
        Return a single metafield value for the given instance (or default).

        Args:
            instance: The model instance to get metafield for
            namespace: Metafield namespace
            key: Metafield key within namespace
            default: Default value if metafield doesn't exist

        Returns:
            The metafield value or default if not found
        """
        try:
            definition = MetafieldDefinition.objects.get(
                store=instance.store, namespace=namespace, key=key
            )
            metafield = MetafieldService.get_metafield(instance, definition)
            if metafield:
                return metafield.get_value()
            return default
        except MetafieldDefinition.DoesNotExist:
            return default

    @staticmethod
    def set_metafield(instance, namespace, key, value, **options):
        """
        Create or update a metafield value for the given instance.

        Args:
            instance: The model instance to set metafield for
            namespace: Metafield namespace
            key: Metafield key within namespace
            value: The value to set
            **options: Additional options (type, required, etc.)

        Returns:
            The created or updated Metafield instance
        """
        # Get or create definition with options
        defaults = {
            "name": f"{namespace}.{key}",
            "type": options.get("type", MetafieldService._infer_type(value)),
            "content_types": [ContentType.objects.get_for_model(instance).model],
        }
        defaults.update(options)

        definition, created = MetafieldDefinition.objects.get_or_create(
            store=instance.store,
            namespace=namespace,
            key=key,
            defaults=defaults,
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
    def get_all_metafields(instance):
        """
        Return all metafields for the given instance as a dict
        keyed by "namespace.key".

        Args:
            instance: The model instance to get metafields for

        Returns:
            Dict with format {"namespace.key": {"type": "...", "value": ...}, ...}
        """
        metafields = {}
        queryset = MetafieldService.get_metafields_for_object(instance)

        for metafield in queryset:
            key = f"{metafield.definition.namespace}.{metafield.definition.key}"
            metafields[key] = {
                "type": metafield.definition.type,
                "value": metafield.get_value(),
            }

        return metafields

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


def serialize_metafields_for_instance(instance):
    """
    Return a dictionary of metafields for the given instance in a
    normalized shape:

    {
        "namespace.key": {
            "type": "...",
            "value": ...,
        },
        ...
    }

    Uses MetafieldService.get_all_metafields() internally to ensure
    consistent serialization across all APIs.

    Args:
        instance: The model instance to serialize metafields for

    Returns:
        Dict with standardized metafields shape
    """
    return MetafieldService.get_all_metafields(instance)
