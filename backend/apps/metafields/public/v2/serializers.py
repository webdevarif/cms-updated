"""
Serializers for public metafields module.
"""

from apps.metafields.models import Metafield, MetafieldDefinition
from rest_framework import serializers


class MetafieldPublicSerializer(serializers.ModelSerializer):
    """
    Architectural + real implementation for public metafields interface.

    Read-only serializer for public metafield consumption.
    Only includes visible fields and excludes sensitive data.
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
