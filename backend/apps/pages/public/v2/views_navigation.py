"""
Public navigation views - read-only interface for menus.
"""

from apps.pages.models import Menu
from apps.pages.services.navigation_service import NavigationService
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers_navigation import MenuPublicSerializer


class MenuPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public menu API - read-only access to store menus.

    Provides:
    - List all menus for a store
    - Retrieve menu by ID with nested items
    - Get default menu for store
    """

    permission_classes = [AllowAny]  # Public access
    serializer_class = MenuPublicSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
    filterset_fields = ["is_default"]

    def get_queryset(self):
        """Filter to store menus."""
        store = getattr(self.request, "store", None)
        if not store:
            return Menu.objects.none()

        return Menu.objects.filter(store=store).prefetch_related("items")

    @action(detail=False, methods=["get"])
    def default(self, request):
        """
        Get the default menu for the store.

        Returns the default menu with nested items, or 404 if no default exists.
        """
        store = getattr(self.request, "store", None)
        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            default_menu = NavigationService.get_default_menu(store)
            if not default_menu:
                return Response(
                    {"error": "No default menu found"}, status=status.HTTP_404_NOT_FOUND
                )

            serializer = self.get_serializer(default_menu)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["get"])
    def tree(self, request, pk=None):
        """
        Get menu items in tree structure for this menu.

        Returns a nested tree structure suitable for frontend navigation.
        """
        menu = self.get_object()
        try:
            tree = NavigationService.build_menu_tree(menu)
            return Response({"items": tree}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
