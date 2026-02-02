"""
Public navigation serializers - read-only interface for menus.
"""

from apps.pages.models import Menu, MenuItem
from rest_framework import serializers


class MenuItemPublicSerializer(serializers.ModelSerializer):
    """Public menu item serializer with limited fields for read-only access."""

    page = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()
    link_type = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = [
            "id",
            "title",
            "page",
            "url",
            "link",
            "link_type",
            "position",
            "children",
        ]
        read_only_fields = fields

    def get_page(self, obj):
        """Return page data if available."""
        if obj.page:
            return {
                "id": obj.page.id,
                "title": obj.page.title,
                "slug": obj.page.slug,
                "url": obj.get_link(),
            }
        return None

    def get_link(self, obj):
        """Get the actual link for this menu item."""
        return obj.get_link()

    def get_link_type(self, obj):
        """Get the type of link: 'page' or 'url'."""
        return obj.get_link_type()

    def get_children(self, obj):
        """Get child items recursively."""
        children = obj.children.filter(is_visible=True).order_by("position", "created_at")
        return MenuItemPublicSerializer(children, many=True, context=self.context).data


class MenuPublicSerializer(serializers.ModelSerializer):
    """Public menu serializer with nested items for read-only access."""

    items = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = [
            "id",
            "name",
            "slug",
            "is_default",
            "items",
        ]
        read_only_fields = fields

    def get_items(self, obj):
        """Get menu items in tree structure."""
        from apps.pages.services.navigation_service import NavigationService

        return NavigationService.build_menu_tree(obj)
