"""
Public entities serializers - read-only interface for entity interactions.
"""
from apps.entities.models import EntityAction, EntityInteraction
from rest_framework import serializers


class PublicEntityActionSerializer(serializers.ModelSerializer):
    """Public entity action serializer with limited fields."""

    interaction_count = serializers.SerializerMethodField()

    class Meta:
        model = EntityAction
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "action_type",
            "icon",
            "color",
            "is_public",
            "allow_anonymous",
            "interaction_count",
        ]
        read_only_fields = fields

    def get_interaction_count(self, obj):
        """Get interaction count for this action."""
        return EntityInteraction.objects.filter(action=obj, is_active=True).count()


class PublicEntityInteractionSerializer(serializers.ModelSerializer):
    """Public entity interaction serializer with limited fields."""

    action_name = serializers.CharField(source="action.name", read_only=True)
    action_slug = serializers.CharField(source="action.slug", read_only=True)
    action_type = serializers.CharField(source="action.action_type", read_only=True)
    action_icon = serializers.CharField(source="action.icon", read_only=True)
    action_color = serializers.CharField(source="action.color", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    content_type_name = serializers.CharField(source="content_type.model", read_only=True)

    class Meta:
        model = EntityInteraction
        fields = [
            "id",
            "action_name",
            "action_slug",
            "action_type",
            "action_icon",
            "action_color",
            "username",
            "content_type",
            "object_id",
            "content_type_name",
            "value",
            "rating",
            "created_at",
        ]
        read_only_fields = fields


class PublicEntityStatsSerializer(serializers.Serializer):
    """Public entity statistics serializer."""

    name = serializers.CharField(read_only=True)
    action_type = serializers.CharField(read_only=True)
    interaction_count = serializers.IntegerField(read_only=True)
    icon = serializers.CharField(read_only=True)
    color = serializers.CharField(read_only=True)


class PublicEntitySummarySerializer(serializers.Serializer):
    """Public entity summary serializer."""

    content_type = serializers.CharField(read_only=True)
    object_id = serializers.IntegerField(read_only=True)
    actions = serializers.DictField(read_only=True)
