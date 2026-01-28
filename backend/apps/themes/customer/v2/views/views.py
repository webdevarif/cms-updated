"""
Customer themes API views - authenticated theme management and customization.
"""
from apps.themes.models import Theme
from apps.themes.services import ThemeService
from core.permissions import IsAuthenticatedAndStoreOwner
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..serializers.serializers import ThemeCustomerSerializer


class ThemeCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer theme API - authenticated users can view and customize themes.
    Provides theme management, settings, custom CSS/JS, and preview functionality.
    """

    permission_classes = [IsAuthenticatedAndStoreOwner]
    queryset = Theme.objects.filter(is_active=True)
    serializer_class = ThemeCustomerSerializer

    def get_queryset(self):
        """Filter themes available to user's store"""
        # Show all active themes plus store's custom themes
        base_queryset = super().get_queryset()
        store = getattr(self.request, "store", None)
        if store:
            # Include store-specific custom themes
            custom_themes = Theme.objects.filter(created_by=self.request.user, store=store)
            return (base_queryset | custom_themes).distinct()
        return base_queryset

    @action(detail=True, methods=["post"])
    def apply_theme(self, request, pk=None):
        """
        Apply a theme to the authenticated user's store.
        Sets the theme as active for the store.
        """
        theme = self.get_object()
        store = getattr(request, "store", None)

        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Apply theme to store
            ThemeService.apply_theme_to_store(theme=theme, store=store, user=request.user)

            return Response(
                {
                    "message": f'Theme "{theme.name}" applied successfully',
                    "theme": ThemeCustomerSerializer(theme).data,
                }
            )

        except Exception as e:
            return Response(
                {"error": f"Theme application failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def preview_theme(self, request, pk=None):
        """
        Preview a theme with custom settings before applying.
        Returns rendered HTML preview.
        """
        theme = self.get_object()
        preview_settings = request.data.get("settings", {})
        preview_content = request.data.get("content", {})

        try:
            # Generate preview with custom settings
            preview_data = ThemeCustomizationService.generate_theme_preview(
                theme=theme,
                settings=preview_settings,
                content=preview_content,
                store=request.store if hasattr(request, "store") else None,
                user=request.user,
            )

            serializer = ThemePreviewSerializer(preview_data)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": f"Preview generation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"])
    def settings(self, request, pk=None):
        """
        Get current theme settings for the authenticated user's store.
        """
        theme = self.get_object()
        store = getattr(request, "store", None)

        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get theme settings for store
            settings = ThemeCustomizationService.get_theme_settings(theme=theme, store=store)

            return Response({"theme": theme.slug, "settings": settings})

        except Exception as e:
            return Response(
                {"error": f"Settings retrieval failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["put"])
    def update_settings(self, request, pk=None):
        """
        Update theme settings for the authenticated user's store.
        Allows customization of colors, fonts, spacing, etc.
        """
        theme = self.get_object()
        store = getattr(request, "store", None)
        settings_data = request.data.get("settings", {})

        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate and update theme settings
            updated_settings = ThemeCustomizationService.update_theme_settings(
                theme=theme, store=store, settings=settings_data, user=request.user
            )

            return Response(
                {"message": "Theme settings updated successfully", "settings": updated_settings}
            )

        except Exception as e:
            return Response(
                {"error": f"Settings update failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def add_custom_css(self, request, pk=None):
        """
        Add custom CSS to a theme for the authenticated user's store.
        """
        theme = self.get_object()
        store = getattr(request, "store", None)
        css_content = request.data.get("css", "")

        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        if not css_content:
            return Response(
                {"error": "CSS content is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Add custom CSS to theme
            ThemeCustomizationService.add_custom_css(
                theme=theme, store=store, css_content=css_content, user=request.user
            )

            return Response({"message": "Custom CSS added successfully"})

        except Exception as e:
            return Response(
                {"error": f"Custom CSS addition failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def add_custom_js(self, request, pk=None):
        """
        Add custom JavaScript to a theme for the authenticated user's store.
        """
        theme = self.get_object()
        store = getattr(request, "store", None)
        js_content = request.data.get("js", "")

        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        if not js_content:
            return Response(
                {"error": "JavaScript content is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Add custom JS to theme
            ThemeCustomizationService.add_custom_js(
                theme=theme, store=store, js_content=js_content, user=request.user
            )

            return Response({"message": "Custom JavaScript added successfully"})

        except Exception as e:
            return Response(
                {"error": f"Custom JavaScript addition failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def current_theme(self, request):
        """
        Get the currently active theme for the authenticated user's store.
        """
        store = getattr(request, "store", None)

        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get current theme for store
            current_theme = ThemeCustomizationService.get_current_theme(store)

            if current_theme:
                serializer = ThemeCustomerSerializer(current_theme)
                return Response(
                    {
                        "current_theme": serializer.data,
                        "settings": ThemeCustomizationService.get_theme_settings(
                            current_theme, store
                        ),
                    }
                )
            else:
                return Response({"current_theme": None, "message": "No theme is currently active"})

        except Exception as e:
            return Response(
                {"error": f"Current theme retrieval failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def create_custom_theme(self, request):
        """
        Create a custom theme based on an existing theme for the authenticated user.
        """
        base_theme_id = request.data.get("base_theme_id")
        theme_name = request.data.get("name", "")
        theme_description = request.data.get("description", "")

        if not base_theme_id:
            return Response(
                {"error": "base_theme_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not theme_name:
            return Response({"error": "name is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get base theme
            base_theme = Theme.objects.get(id=base_theme_id, is_active=True)

            # Create custom theme
            custom_theme = ThemeCustomizationService.create_custom_theme(
                base_theme=base_theme,
                name=theme_name,
                description=theme_description,
                store=request.store if hasattr(request, "store") else None,
                user=request.user,
            )

            serializer = ThemeCustomerSerializer(custom_theme)
            return Response(
                {"message": "Custom theme created successfully", "theme": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        except Theme.DoesNotExist:
            return Response({"error": "Base theme not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": f"Custom theme creation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
