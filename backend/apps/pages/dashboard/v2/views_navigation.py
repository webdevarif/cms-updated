"""
Dashboard navigation views - full admin interface for menu management.
"""

from apps.pages.models import Menu, MenuItem
from apps.pages.services.navigation_service import NavigationService
from core.permissions import IsStoreOwner
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers_navigation import (
    MenuDashboardSerializer,
    MenuItemDashboardSerializer,
    MenuReorderSerializer,
)


class MenuDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard menu API - full admin CRUD on store menus.

    Provides:
    - List all menus in store
    - Create/update/delete menus
    - Set default menu
    - Get menu with items
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = MenuDashboardSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "created_at", "updated_at"]
    ordering = ["name"]
    filterset_fields = ["is_default"]

    def get_queryset(self):
        """Filter to store menus."""
        store = getattr(self.request, "store", None)
        return Menu.objects.filter(store=store).prefetch_related("items")

    def perform_create(self, serializer):
        """Set store when creating menu."""
        serializer.save(store=getattr(self.request, "store", None))

    @action(detail=True, methods=["post"])
    def set_default(self, request, pk=None):
        """
        Set this menu as the default menu for the store.
        """
        menu = self.get_object()
        try:
            NavigationService.set_default_menu(menu.store, menu)
            return Response(
                {"message": f"'{menu.name}' set as default menu"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["get"])
    def items(self, request, pk=None):
        """
        Get all menu items for this menu in tree structure.
        """
        menu = self.get_object()
        try:
            tree = NavigationService.build_menu_tree(menu)
            return Response({"items": tree}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MenuItemDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard menu item API - full admin CRUD on menu items.

    Provides:
    - List all menu items in store
    - Create/update/delete menu items
    - Reorder menu items
    - Handle parent-child relationships
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = MenuItemDashboardSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["title", "url"]
    ordering_fields = ["position", "title", "created_at"]
    ordering = ["position", "created_at"]
    filterset_fields = ["menu", "parent", "is_visible"]

    def get_queryset(self):
        """Filter to store menu items."""
        store = getattr(self.request, "store", None)
        return MenuItem.objects.filter(menu__store=store).select_related("menu", "parent", "page")

    @action(detail=False, methods=["post"])
    def reorder(self, request):
        """
        Reorder menu items based on provided positions.

        Expected payload:
        {
            "items": [
                {"id": 1, "position": 0},
                {"id": 2, "position": 1},
                {"id": 3, "position": 2}
            ]
        }
        """
        serializer = MenuReorderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            items_data = serializer.validated_data["items"]
            menu_item_orders = [(item["id"], item["position"]) for item in items_data]

            NavigationService.reorder_menu_items(menu_item_orders)

            return Response(
                {"message": "Menu items reordered successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["post"])
    def move_up(self, request, pk=None):
        """
        Move this menu item up in the ordering.
        """
        menu_item = self.get_object()
        try:
            # Find the previous item in the same menu and parent
            previous_item = (
                MenuItem.objects.filter(
                    menu=menu_item.menu,
                    parent=menu_item.parent,
                    position__lt=menu_item.position,
                )
                .order_by("-position")
                .first()
            )

            if previous_item:
                # Swap positions
                menu_item.position, previous_item.position = (
                    previous_item.position,
                    menu_item.position,
                )
                menu_item.save(update_fields=["position"])
                previous_item.save(update_fields=["position"])

                return Response(
                    {"message": "Menu item moved up successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Menu item is already at the top"},
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["post"])
    def move_down(self, request, pk=None):
        """
        Move this menu item down in the ordering.
        """
        menu_item = self.get_object()
        try:
            # Find the next item in the same menu and parent
            next_item = (
                MenuItem.objects.filter(
                    menu=menu_item.menu,
                    parent=menu_item.parent,
                    position__gt=menu_item.position,
                )
                .order_by("position")
                .first()
            )

            if next_item:
                # Swap positions
                menu_item.position, next_item.position = (
                    next_item.position,
                    menu_item.position,
                )
                menu_item.save(update_fields=["position"])
                next_item.save(update_fields=["position"])

                return Response(
                    {"message": "Menu item moved down successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Menu item is already at the bottom"},
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
