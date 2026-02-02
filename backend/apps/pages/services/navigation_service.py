"""
Navigation service for building menu trees and future enhancements.
"""

import logging

logger = logging.getLogger(__name__)


class NavigationService:
    """Service for navigation operations and tree building."""

    @staticmethod
    def build_menu_tree(menu):
        """
        Build a nested tree structure for menu items.

        Args:
            menu: Menu instance

        Returns:
            List of menu items in nested tree format
        """
        from ..models import MenuItem

        # Get all menu items ordered by position
        items = (
            MenuItem.objects.filter(menu=menu, is_visible=True)
            .select_related("page", "parent")
            .order_by("position", "created_at")
        )

        # Build tree structure
        items_dict = {}
        root_items = []

        # First pass: create all items
        for item in items:
            item_data = {
                "id": item.id,
                "title": item.title,
                "url": item.url,
                "page": None,
                "position": item.position,
                "children": [],
            }

            # Add page data if available
            if item.page:
                item_data["page"] = {
                    "id": item.page.id,
                    "title": item.page.title,
                    "slug": item.page.slug,
                    "url": item.get_link(),
                }
                item_data["url"] = None  # Clear URL if page is set

            items_dict[item.id] = item_data

        # Second pass: build hierarchy
        for item in items:
            item_data = items_dict[item.id]

            if item.parent is None:
                root_items.append(item_data)
            else:
                parent_data = items_dict.get(item.parent.id)
                if parent_data:
                    parent_data["children"].append(item_data)

        return root_items

    @staticmethod
    def get_store_menus(store):
        """
        Get all menus for a store with their items.

        Args:
            store: Store instance

        Returns:
            QuerySet of menus for the store
        """
        from ..models import Menu

        return Menu.objects.filter(store=store).order_by("name")

    @staticmethod
    def get_default_menu(store):
        """
        Get the default menu for a store.

        Args:
            store: Store instance

        Returns:
            Menu instance or None
        """
        from ..models import Menu

        return Menu.objects.filter(store=store, is_default=True).first()

    @staticmethod
    def set_default_menu(store, menu):
        """
        Set a menu as the default for a store.

        Args:
            store: Store instance
            menu: Menu instance
        """
        from ..models import Menu

        # Clear existing default
        Menu.objects.filter(store=store, is_default=True).update(is_default=False)

        # Set new default
        menu.is_default = True
        menu.save(update_fields=["is_default"])

    @staticmethod
    def reorder_menu_items(menu_item_orders):
        """
        Reorder menu items based on provided positions.

        Args:
            menu_item_orders: List of tuples (item_id, position)
        """
        from ..models import MenuItem

        for item_id, position in menu_item_orders:
            MenuItem.objects.filter(id=item_id).update(position=position)

    @staticmethod
    def validate_menu_item_data(data, menu=None, exclude_item=None):
        """
        Validate menu item data before creation/update.

        Args:
            data: Dictionary of menu item data
            menu: Menu instance (for validation)
            exclude_item: MenuItem instance to exclude from validation (for updates)

        Raises:
            ValidationError: If data is invalid
        """
        from django.core.exceptions import ValidationError

        from ..models import MenuItem

        # Check that either page or url is provided
        page = data.get("page")
        url = data.get("url")

        if page and url:
            raise ValidationError("A menu item can have either a page or a URL, but not both.")

        if not page and not url:
            raise ValidationError("A menu item must have either a page or a URL.")

        # Validate page is actually a page post type
        if page:
            from apps.posts.models import PostType

            page_type_slug = page.post_type.slug if page.post_type else None
            if page_type_slug != "page":
                raise ValidationError("Only pages can be linked to menu items.")

        # Validate parent belongs to same menu
        parent_id = data.get("parent")
        if parent_id and menu:
            try:
                parent = MenuItem.objects.get(id=parent_id, menu=menu)
                if exclude_item and parent.id == exclude_item.id:
                    raise ValidationError("Cannot set an item as its own parent.")
            except MenuItem.DoesNotExist:
                raise ValidationError("Parent menu item not found or belongs to different menu.")

        return True
