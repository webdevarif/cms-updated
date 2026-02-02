"""
Dashboard entities serializers - admin interface for entity management.
"""

from apps.entities.models import EntityAction, EntityInteraction
from rest_framework import serializers


class DashboardEntityActionSerializer(serializers.ModelSerializer):
    """Dashboard entity action serializer for admin access."""

    interaction_count = serializers.SerializerMethodField()
    active_interaction_count = serializers.SerializerMethodField()
    unique_user_count = serializers.SerializerMethodField()

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
            "content_types",
            "is_active",
            "is_public",
            "allow_anonymous",
            "metadata",
            "store",
            "interaction_count",
            "active_interaction_count",
            "unique_user_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "interaction_count",
            "active_interaction_count",
            "unique_user_count",
        ]

    def get_interaction_count(self, obj):
        """Get total interaction count."""
        return EntityInteraction.objects.filter(action=obj).count()

    def get_active_interaction_count(self, obj):
        """Get active interaction count."""
        return EntityInteraction.objects.filter(action=obj, is_active=True).count()

    def get_unique_user_count(self, obj):
        """Get unique user count."""
        return (
            EntityInteraction.objects.filter(action=obj, is_active=True)
            .values("user")
            .distinct()
            .count()
        )


class DashboardEntityActionCreateSerializer(serializers.ModelSerializer):
    """Dashboard entity action creation serializer."""

    class Meta:
        model = EntityAction
        fields = [
            "name",
            "slug",
            "description",
            "action_type",
            "icon",
            "color",
            "content_types",
            "is_active",
            "is_public",
            "allow_anonymous",
            "metadata",
        ]

    def validate_slug(self, value):
        """Validate slug is unique for the store."""
        request = self.context.get("request")
        store = getattr(request, "store", None)

        if store and EntityAction.objects.filter(store=store, slug=value).exists():
            raise serializers.ValidationError("Slug must be unique for this store")

        return value


class DashboardEntityInteractionSerializer(serializers.ModelSerializer):
    """Dashboard entity interaction serializer for admin access."""

    action_name = serializers.CharField(source="action.name", read_only=True)
    action_slug = serializers.CharField(source="action.slug", read_only=True)
    action_type = serializers.CharField(source="action.action_type", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    content_type_name = serializers.CharField(source="content_type.model", read_only=True)

    class Meta:
        model = EntityInteraction
        fields = [
            "id",
            "action",
            "action_name",
            "action_slug",
            "action_type",
            "user",
            "username",
            "user_email",
            "content_type",
            "object_id",
            "content_type_name",
            "value",
            "rating",
            "is_active",
            "ip_address",
            "user_agent",
            "store",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "ip_address",
            "user_agent",
        ]


class DashboardEntityAnalyticsSerializer(serializers.Serializer):
    """Dashboard entity analytics serializer."""

    total_interactions = serializers.IntegerField()
    active_interactions = serializers.IntegerField()
    unique_users = serializers.IntegerField()
    actions_summary = serializers.ListField(child=serializers.DictField())
    content_types_summary = serializers.ListField(child=serializers.DictField())
    monthly_trends = serializers.ListField(child=serializers.DictField())
    top_users = serializers.ListField(child=serializers.DictField())


class DashboardEntityActionStatsSerializer(serializers.Serializer):
    """Dashboard entity action stats serializer."""

    total_interactions = serializers.IntegerField()
    active_interactions = serializers.IntegerField()
    unique_users = serializers.IntegerField()
    average_rating = serializers.FloatField()
    interactions_by_content_type = serializers.ListField(child=serializers.DictField())
    recent_interactions = serializers.ListField(child=serializers.DictField())


class DashboardBulkInteractionSerializer(serializers.Serializer):
    """Dashboard bulk interaction operations serializer."""

    interaction_ids = serializers.ListField(
        child=serializers.IntegerField(), min_length=1, max_length=1000
    )

    def validate_interaction_ids(self, value):
        """Validate interaction IDs exist."""
        request = self.context.get("request")
        store = getattr(request, "store", None)

        if store:
            existing_ids = EntityInteraction.objects.filter(id__in=value, store=store).values_list(
                "id", flat=True
            )

            missing_ids = set(value) - set(existing_ids)
            if missing_ids:
                raise serializers.ValidationError(f"Interaction IDs not found: {list(missing_ids)}")

        return value


class DashboardEntityInteractionUpdateSerializer(serializers.ModelSerializer):
    """Dashboard entity interaction update serializer."""

    class Meta:
        model = EntityInteraction
        fields = ["value", "rating", "is_active"]

    def validate_rating(self, value):
        """Validate rating is within valid range."""
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
