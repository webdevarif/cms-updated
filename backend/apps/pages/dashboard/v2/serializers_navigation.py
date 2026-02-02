"""
Dashboard navigation serializers - full admin interface for menu management.
"""

from apps.pages.models import Menu, MenuItem
from rest_framework import serializers


class MenuItemDashboardSerializer(serializers.ModelSerializer):
    """Dashboard menu item serializer with full admin fields."""

    page_title = serializers.CharField(source="page.title", read_only=True)
    page_slug = serializers.CharField(source="page.slug", read_only=True)
    parent_title = serializers.CharField(source="parent.title", read_only=True)
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = [
            "id",
            "menu",
            "parent",
            "title",
            "url",
            "page",
            "page_title",
            "page_slug",
            "parent_title",
            "position",
            "is_visible",
            "children_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "page_title",
            "page_slug",
            "parent_title",
            "children_count",
        ]

    def get_children_count(self, obj):
        """Get the number of child items."""
        return obj.children.count()

    def validate(self, data):
        """Custom validation for menu item."""
        from apps.pages.services.navigation_service import NavigationService

        # Use NavigationService for validation
        NavigationService.validate_menu_item_data(
            data,
            menu=data.get("menu"),
            exclude_item=self.instance if self.instance else None,
        )

        return data

    def create(self, validated_data):
        """Create menu item with logging."""
        from apps.analytics.services.event_service import EventService

        menu_item = super().create(validated_data)

        # Log menu creation
        EventService.log_event(
            event_type="MENU_ITEM_CREATED",
            event_name=f"Menu item created: {menu_item.title}",
            properties={
                "user": validated_data.get("user", None),
                "store": validated_data.get("store", None),
                "entity_type": "MenuItem",
                "entity_id": menu_item.id,
                "title": menu_item.title,
                "page_id": str(menu_item.page.id) if menu_item.page else None,
                "url": menu_item.url,
                "position": menu_item.position,
            },
            user=validated_data.get("user"),
            store=validated_data.get("store"),
        )

        return menu_item

    def update(self, instance, validated_data):
        """Update menu item with logging."""
        from apps.analytics.services.event_service import EventService

        old_title = instance.title
        old_position = instance.position

        # Use NavigationService for validation
        from apps.pages.services.navigation_service import NavigationService

        NavigationService.validate_menu_item_data(
            validated_data, menu=instance.menu, exclude_item=instance
        )

        menu_item = super().update(instance, validated_data)

        # Log menu update
        EventService.log_event(
            event_type="MENU_ITEM_UPDATED",
            event_name=f"Menu item updated: {menu_item.title}",
            properties={
                "user": validated_data.get("user", None),
                "store": validated_data.get("store", None),
                "entity_type": "MenuItem",
                "entity_id": menu_item.id,
                "old_title": old_title,
                "new_title": menu_item.title,
                "old_position": old_position,
                "new_position": menu_item.position,
            },
            user=validated_data.get("user"),
            store=validated_data.get("store"),
        )

        return menu_item


class MenuDashboardSerializer(serializers.ModelSerializer):
    """Dashboard menu serializer with full admin fields."""

    store_name = serializers.CharField(source="store.name", read_only=True)
    items_count = serializers.SerializerMethodField()
    items = MenuItemDashboardSerializer(many=True, read_only=True)

    class Meta:
        model = Menu
        fields = [
            "id",
            "store",
            "store_name",
            "name",
            "slug",
            "is_default",
            "items_count",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "store",
            "store_name",
            "created_at",
            "updated_at",
            "items_count",
        ]

    def get_items_count(self, obj):
        """Get the total number of items in this menu."""
        return obj.items.count()

    def create(self, validated_data):
        """Create menu with logging."""
        from apps.analytics.services.event_service import EventService

        menu = super().create(validated_data)

        # Log menu creation
        EventService.log_event(
            event_type="MENU_CREATED",
            event_name=f"Menu created: {menu.name}",
            properties={
                "user": validated_data.get("user", None),
                "store": validated_data.get("store", None),
                "entity_type": "Menu",
                "entity_id": menu.id,
                "name": menu.name,
                "is_default": menu.is_default,
            },
            user=validated_data.get("user"),
            store=validated_data.get("store"),
        )

        return menu

    def update(self, instance, validated_data):
        """Update menu with logging."""
        from apps.analytics.services.event_service import EventService

        old_name = instance.name
        old_is_default = instance.is_default

        menu = super().update(instance, validated_data)

        # Log menu update
        EventService.log_event(
            event_type="MENU_UPDATED",
            event_name=f"Menu updated: {menu.name}",
            properties={
                "user": validated_data.get("user", None),
                "store": validated_data.get("store", None),
                "entity_type": "Menu",
                "entity_id": menu.id,
                "old_name": old_name,
                "new_name": menu.name,
                "old_is_default": old_is_default,
                "new_is_default": menu.is_default,
            },
            user=validated_data.get("user"),
            store=validated_data.get("store"),
        )

        return menu

    def delete(self, instance):
        """Delete menu with logging."""
        from apps.analytics.services.event_service import EventService

        # Log menu deletion
        EventService.log_event(
            event_type="MENU_DELETED",
            event_name=f"Menu deleted: {instance.name}",
            properties={
                "user": self.context["request"].user,
                "store": instance.store,
                "entity_type": "Menu",
                "entity_id": instance.id,
                "name": instance.name,
                "is_default": instance.is_default,
            },
            user=self.context["request"].user,
            store=instance.store,
        )

        return super().delete(instance)


class MenuReorderSerializer(serializers.Serializer):
    """Serializer for reordering menu items."""

    items = serializers.ListField(child=serializers.DictField(child=serializers.IntegerField()))

    def validate_items(self, value):
        """Validate the items list format."""
        for item in value:
            if "id" not in item or "position" not in item:
                raise serializers.ValidationError("Each item must have 'id' and 'position' fields.")
        return value
