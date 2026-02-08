"""
Serializers for customer metafields module.
"""

from apps.metafields.models import Metafield, MetafieldDefinition
from rest_framework import serializers

from django.contrib.contenttypes.models import ContentType


class MetafieldCustomerSerializer(serializers.ModelSerializer):
    """
    Architectural + real implementation for customer metafields interface.

    Full CRUD serializer for authenticated users managing their metafields.
    """

    key = serializers.CharField(source="definition.key", read_only=True)
    name = serializers.CharField(source="definition.name", read_only=True)
    type = serializers.CharField(source="definition.type", read_only=True)
    namespace = serializers.CharField(source="definition.namespace", read_only=True)

    class Meta:
        model = Metafield
        fields = [
            "id",
            "key",
            "name",
            "type",
            "namespace",
            "content_type",
            "object_id",
            "value_text",
            "value_number",
            "value_boolean",
            "value_date",
            "value_json",
            "value_media",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BulkMetafieldUpdateSerializer(serializers.Serializer):
    """Serializer for bulk updating metafields"""

    content_type = serializers.ChoiceField(
        choices=[],
        help_text="Content type model name (e.g., 'product')",  # Will be set in __init__
    )
    object_id = serializers.IntegerField(help_text="Object ID")
    metafields = serializers.DictField(
        child=serializers.JSONField(),
        help_text="Dictionary of metafield values (namespace.key: value)",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set available content types dynamically
        content_types = ContentType.objects.filter(
            app_label__in=["ecommerce", "posts", "pages", "forms"]
        ).values_list("model", flat=True)
        self.fields["content_type"].choices = [(ct, ct) for ct in content_types]


class BulkMetafieldCreateSerializer(serializers.Serializer):
    """Serializer for bulk creating metafields"""

    content_type = serializers.ChoiceField(
        choices=[],
        help_text="Content type model name (e.g., 'product')",  # Will be set in __init__
    )
    object_id = serializers.IntegerField(help_text="Object ID")
    metafields = serializers.DictField(
        child=serializers.JSONField(),
        help_text="Dictionary of metafield values (namespace.key: value)",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set available content types dynamically
        content_types = ContentType.objects.filter(
            app_label__in=["ecommerce", "posts", "pages", "forms"]
        ).values_list("model", flat=True)
        self.fields["content_type"].choices = [(ct, ct) for ct in content_types]


class BulkMetafieldDeleteSerializer(serializers.Serializer):
    """Serializer for bulk deleting metafields"""

    metafield_ids = serializers.ListField(
        child=serializers.IntegerField(), help_text="List of metafield IDs to delete"
    )
