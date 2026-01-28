"""
Serializers for dashboard metafields module.
"""
from apps.metafields.models import Metafield, MetafieldDefinition
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers


class MetafieldDefinitionDashboardSerializer(serializers.ModelSerializer):
    """
    Architectural + real implementation for dashboard metafield definitions interface.

    Full admin serializer with all fields for metafield definitions.
    """

    class Meta:
        model = MetafieldDefinition
        fields = [
            "id",
            "store",
            "name",
            "namespace",
            "key",
            "type",
            "is_required",
            "is_visible",
            "is_filterable",
            "is_sortable",
            "options",
            "validations",
            "content_types",
            "ui",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "store", "created_at", "updated_at"]


class MetafieldDashboardSerializer(serializers.ModelSerializer):
    """
    Architectural + real implementation for dashboard metafields interface.

    Full admin serializer with all fields for metafield values.
    """

    namespace = serializers.CharField(source="definition.namespace", read_only=True)
    key = serializers.CharField(source="definition.key", read_only=True)
    name = serializers.CharField(source="definition.name", read_only=True)
    type = serializers.CharField(source="definition.type", read_only=True)
    definition = MetafieldDefinitionDashboardSerializer(read_only=True)

    class Meta:
        model = Metafield
        fields = [
            "id",
            "definition",
            "namespace",
            "key",
            "name",
            "type",
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
        choices=[], help_text="Content type model name (e.g., 'product')"  # Will be set in __init__
    )
    object_id = serializers.IntegerField(help_text="Object ID")
    metafields = serializers.DictField(
        child=serializers.JSONField(),
        help_text="Dictionary of metafield values (namespace.key: value)",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set available content types dynamically
        content_types = ContentType.objects.all().values_list("model", flat=True)
        self.fields["content_type"].choices = [(ct, ct) for ct in content_types]


class BulkMetafieldCreateSerializer(serializers.Serializer):
    """Serializer for bulk creating metafields"""

    content_type = serializers.ChoiceField(
        choices=[], help_text="Content type model name (e.g., 'product')"  # Will be set in __init__
    )
    object_id = serializers.IntegerField(help_text="Object ID")
    metafields = serializers.DictField(
        child=serializers.JSONField(),
        help_text="Dictionary of metafield values (namespace.key: value)",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set available content types dynamically
        content_types = ContentType.objects.all().values_list("model", flat=True)
        self.fields["content_type"].choices = [(ct, ct) for ct in content_types]


class BulkMetafieldDeleteSerializer(serializers.Serializer):
    """Serializer for bulk deleting metafields"""

    metafield_ids = serializers.ListField(
        child=serializers.IntegerField(), help_text="List of metafield IDs to delete"
    )


class BulkMetafieldAttachSerializer(serializers.Serializer):
    """Serializer for bulk attaching metafields"""

    content_type = serializers.ChoiceField(
        choices=[], help_text="Content type model name (e.g., 'product')"  # Will be set in __init__
    )
    object_id = serializers.IntegerField(help_text="Object ID")
    metafields = serializers.DictField(
        child=serializers.JSONField(),
        help_text="Dictionary of metafield values (namespace.key: value)",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set available content types dynamically
        content_types = ContentType.objects.all().values_list("model", flat=True)
        self.fields["content_type"].choices = [(ct, ct) for ct in content_types]


class BulkMetafieldDetachSerializer(serializers.Serializer):
    """Serializer for bulk detaching metafields"""

    content_type = serializers.ChoiceField(
        choices=[], help_text="Content type model name (e.g., 'product')"  # Will be set in __init__
    )
    object_id = serializers.IntegerField(help_text="Object ID")
    metafields = serializers.ListField(
        child=serializers.CharField(), help_text="List of metafield keys to detach"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set available content types dynamically
        content_types = ContentType.objects.all().values_list("model", flat=True)
        self.fields["content_type"].choices = [(ct, ct) for ct in content_types]
