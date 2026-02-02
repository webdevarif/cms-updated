"""
Customer pages serializers - authenticated user manages own pages.
Architectural + real implementation for customer pages interface.
"""

from apps.pages.models.pages import Post, PostType
from rest_framework import serializers


class PageCustomerSerializer(serializers.ModelSerializer):
    """Customer page serializer for managing own pages."""

    featured_image = serializers.SerializerMethodField()
    post_type_name = serializers.CharField(source="post_type.name", read_only=True)

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
            "meta_title",
            "meta_description",
            "meta_keywords",
            "created_at",
            "updated_at",
            "author",
        ]
        read_only_fields = [
            "id",
            "author",
            "created_at",
            "updated_at",
            "post_type_name",
        ]

    def get_featured_image(self, obj):
        """Return featured image URL or null."""
        if obj.featured_image:
            return obj.featured_image.url
        return None

    def create(self, validated_data):
        """Create page using PageService."""
        from apps.pages.services.page_service import PageService

        request = self.context.get("request")
        store = getattr(request, "store", None)

        # Remove fields that will be set by service
        data = validated_data.copy()
        data.pop("author", None)

        page = PageService.create_page(store=store, author=request.user, data=data)

        return page

    def update(self, instance, validated_data):
        """Update page using PageService."""
        from apps.pages.services.page_service import PageService

        # Remove fields that shouldn't be updated directly
        data = validated_data.copy()
        data.pop("author", None)

        page = PageService.update_page(instance, data)
        return page


class PageCustomerListSerializer(serializers.ModelSerializer):
    """Simplified customer page serializer for list views."""

    featured_image = serializers.SerializerMethodField()
    post_type_name = serializers.CharField(source="post_type.name", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "status",
            "excerpt",
            "featured_image",
            "post_type_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_featured_image(self, obj):
        """Return featured image URL or null."""
        if obj.featured_image:
            return obj.featured_image.url
        return None
