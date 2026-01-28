"""
Dashboard pages serializers - full admin interface for page management.
Architectural + real implementation for dashboard pages interface.
"""
from apps.pages.models.pages import Post, PostType, Taxonomy, Term
from rest_framework import serializers


class PageDashboardSerializer(serializers.ModelSerializer):
    """Dashboard page serializer with full admin fields."""

    featured_image = serializers.SerializerMethodField()
    post_type_name = serializers.CharField(source="post_type.name", read_only=True)
    author_email = serializers.CharField(source="author.email", read_only=True)
    store_name = serializers.CharField(source="store.name", read_only=True)
    categories = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "excerpt",
            "status",
            "featured_image",
            "post_type",
            "post_type_name",
            "author",
            "author_email",
            "store",
            "store_name",
            "categories",
            "tags",
            "custom_fields",
            "meta_title",
            "meta_description",
            "meta_keywords",
            "published_at",
            "scheduled_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "author",
            "author_email",
            "store",
            "store_name",
            "post_type_name",
            "created_at",
            "updated_at",
        ]

    def get_featured_image(self, obj):
        """Return featured image URL or null."""
        if obj.featured_image:
            return obj.featured_image.url
        return None

    def get_categories(self, obj):
        """Return categories associated with the page."""
        return [{"id": cat.id, "name": cat.name, "slug": cat.slug} for cat in obj.categories.all()]

    def get_tags(self, obj):
        """Return tags associated with the page."""
        return [{"id": tag.id, "name": tag.name, "slug": tag.slug} for tag in obj.tags.all()]


class PageDashboardListSerializer(serializers.ModelSerializer):
    """Simplified dashboard page serializer for list views."""

    featured_image = serializers.SerializerMethodField()
    post_type_name = serializers.CharField(source="post_type.name", read_only=True)
    author_email = serializers.CharField(source="author.email", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "status",
            "excerpt",
            "featured_image",
            "post_type",
            "post_type_name",
            "author",
            "author_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_featured_image(self, obj):
        """Return featured image URL or null."""
        if obj.featured_image:
            return obj.featured_image.url
        return None


class PostTypeSerializer(serializers.ModelSerializer):
    """Post type serializer for dashboard management."""

    class Meta:
        model = PostType
        fields = [
            "id",
            "name",
            "slug",
            "store",
            "is_public",
            "is_hierarchical",
            "supports_comments",
            "supports_featured_image",
            "supports_excerpt",
            "supports_custom_fields",
            "supports_categories",
            "supports_tags",
            "is_system",
            "is_deletable",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TaxonomySerializer(serializers.ModelSerializer):
    """Taxonomy serializer for dashboard management."""

    class Meta:
        model = Taxonomy
        fields = [
            "id",
            "name",
            "slug",
            "taxonomy_type",
            "store",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TermSerializer(serializers.ModelSerializer):
    """Term serializer for dashboard management."""

    taxonomy_name = serializers.CharField(source="taxonomy.name", read_only=True)

    class Meta:
        model = Term
        fields = [
            "id",
            "name",
            "slug",
            "taxonomy",
            "taxonomy_name",
            "store",
            "parent",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BulkActionSerializer(serializers.Serializer):
    """Serializer for bulk actions on pages"""

    action = serializers.ChoiceField(
        choices=[
            "publish",
            "unpublish",
            "delete",
            "duplicate",
            "archive",
            "restore",
            "add_tags",
            "remove_tags",
            "status_change",
        ]
    )
    ids = serializers.ListField(
        child=serializers.IntegerField(), help_text="List of page IDs to perform action on"
    )
    data = serializers.DictField(
        required=False,
        help_text="Additional data for actions like tag operations, status changes, etc.",
    )
