"""
Dashboard themes API views - full admin interface for theme management.
"""
from apps.themes.models import Layout, StyleClass, Template, Theme, ThemeMarketplace, Typography
from apps.themes.services import (
    ThemeManagementService,
    ThemeMarketplaceService,
    ThemeRenderingService,
)
from core.permissions import IsStoreAdmin
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    BulkTemplateUpdateSerializer,
    LayoutDashboardSerializer,
    StyleClassDashboardSerializer,
    TemplateDashboardSerializer,
    ThemeAnalyticsSerializer,
    ThemeDashboardSerializer,
    ThemeMarketplaceSerializer,
    TypographyDashboardSerializer,
)


class ThemeDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard theme API - store admins can fully manage themes.
    Provides theme installation, template editing, translation management, marketplace access.
    """

    permission_classes = [IsStoreAdmin]
    serializer_class = ThemeDashboardSerializer

    def get_queryset(self):
        """Return all themes for admin management"""
        return Theme.objects.all().select_related("created_by")

    @action(detail=False, methods=["post"])
    def install_theme(self, request):
        """
        Install a theme from marketplace or upload.
        Supports ZIP uploads and marketplace installations.
        """
        installation_type = request.data.get("type", "upload")  # 'upload' or 'marketplace'
        theme_data = request.data.get("theme_data", {})

        try:
            if installation_type == "upload":
                # Install from ZIP upload
                theme_zip = request.FILES.get("theme_zip")
                if not theme_zip:
                    return Response(
                        {"error": "theme_zip file is required for upload installation"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                theme = ThemeManagementService.install_theme_from_zip(
                    theme_zip=theme_zip, store=request.store, user=request.user, metadata=theme_data
                )

            elif installation_type == "marketplace":
                # Install from marketplace
                marketplace_theme_id = theme_data.get("marketplace_theme_id")
                if not marketplace_theme_id:
                    return Response(
                        {"error": "marketplace_theme_id is required for marketplace installation"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                theme = ThemeMarketplaceService.install_marketplace_theme(
                    marketplace_theme_id=marketplace_theme_id,
                    store=request.store,
                    user=request.user,
                )

            else:
                return Response(
                    {"error": f"Unsupported installation type: {installation_type}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = ThemeDashboardSerializer(theme)
            return Response(
                {"message": "Theme installed successfully", "theme": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": f"Theme installation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a theme for the store"""
        theme = self.get_object()
        store = getattr(request, "store", None)

        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ThemeManagementService.activate_theme_for_store(
                theme=theme, store=store, user=request.user
            )

            return Response({"message": f'Theme "{theme.name}" activated successfully for store'})

        except Exception as e:
            return Response(
                {"error": f"Theme activation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a theme for the store"""
        theme = self.get_object()
        store = getattr(request, "store", None)

        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ThemeManagementService.deactivate_theme_for_store(
                theme=theme, store=store, user=request.user
            )

            return Response({"message": f'Theme "{theme.name}" deactivated successfully'})

        except Exception as e:
            return Response(
                {"error": f"Theme deactivation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        """Create a duplicate of the theme for customization"""
        theme = self.get_object()
        duplicate_name = request.data.get("name", f"{theme.name} (Copy)")

        try:
            duplicated_theme = ThemeManagementService.duplicate_theme(
                theme=theme, name=duplicate_name, user=request.user, store=request.store
            )

            serializer = ThemeDashboardSerializer(duplicated_theme)
            return Response(
                {"message": "Theme duplicated successfully", "theme": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": f"Theme duplication failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def export_theme(self, request, pk=None):
        """Export theme as ZIP file for backup or sharing"""
        theme = self.get_object()

        try:
            export_data = ThemeManagementService.export_theme_to_zip(theme)

            return Response(
                {
                    "message": "Theme exported successfully",
                    "download_url": export_data["download_url"],
                    "file_size": export_data["file_size"],
                }
            )

        except Exception as e:
            return Response(
                {"error": f"Theme export failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def update_translations(self, request, pk=None):
        """Update theme translations for internationalization"""
        theme = self.get_object()
        translations_data = request.data.get("translations", {})

        if not translations_data:
            return Response(
                {"error": "translations data is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            updated_translations = ThemeManagementService.update_theme_translations(
                theme=theme, translations=translations_data, user=request.user
            )

            return Response(
                {
                    "message": "Theme translations updated successfully",
                    "translations": updated_translations,
                }
            )

        except Exception as e:
            return Response(
                {"error": f"Translations update failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get comprehensive theme analytics across all stores"""
        try:
            analytics = ThemeManagementService.get_theme_analytics()
            serializer = ThemeAnalyticsSerializer(analytics)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": f"Analytics retrieval failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def marketplace(self, request):
        """Browse available themes in the marketplace"""
        try:
            marketplace_themes = ThemeMarketplaceService.get_marketplace_themes()
            return Response(
                {
                    "themes": marketplace_themes,
                    "categories": ThemeMarketplaceService.get_marketplace_categories(),
                }
            )

        except Exception as e:
            return Response(
                {"error": f"Marketplace access failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def bulk_template_update(self, request):
        """
        Bulk update templates across multiple themes.
        Useful for applying security patches or feature updates.
        """
        serializer = BulkTemplateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        template_updates = serializer.validated_data["template_updates"]

        try:
            update_results = ThemeManagementService.bulk_update_templates(
                template_updates=template_updates, user=request.user
            )

            return Response(
                {"message": "Bulk template update completed", "results": update_results}
            )

        except Exception as e:
            return Response(
                {"error": f"Bulk template update failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TemplateDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard template API - full CRUD on theme templates.
    Allows editing template content with syntax validation.
    """

    permission_classes = [IsStoreAdmin]
    serializer_class = TemplateDashboardSerializer

    def get_queryset(self):
        return Template.objects.all().select_related("theme")

    @action(detail=True, methods=["post"])
    def validate_syntax(self, request, pk=None):
        """Validate template syntax before saving"""
        template = self.get_object()
        content = request.data.get("content", template.content)

        try:
            is_valid, errors = ThemeRenderingService.validate_template_syntax(content)

            return Response({"is_valid": is_valid, "errors": errors})

        except Exception as e:
            return Response(
                {"error": f"Syntax validation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LayoutDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard layout API - full CRUD on theme layouts.
    """

    permission_classes = [IsStoreAdmin]
    serializer_class = LayoutDashboardSerializer

    def get_queryset(self):
        return Layout.objects.all().select_related("theme")


class StyleClassDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard style class API - full CRUD on theme CSS classes.
    """

    permission_classes = [IsStoreAdmin]
    serializer_class = StyleClassDashboardSerializer

    def get_queryset(self):
        return StyleClass.objects.all().select_related("theme")


class TypographyDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard typography API - full CRUD on theme typography settings.
    """

    permission_classes = [IsStoreAdmin]
    serializer_class = TypographyDashboardSerializer

    def get_queryset(self):
        return Typography.objects.all().select_related("theme")


class ThemeMarketplaceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Dashboard theme marketplace API - browse and manage marketplace themes.
    """

    permission_classes = [IsStoreAdmin]
    serializer_class = ThemeMarketplaceSerializer

    def get_queryset(self):
        return ThemeMarketplace.objects.filter(is_active=True)

    @action(detail=True, methods=["post"])
    def purchase(self, request, pk=None):
        """Purchase a marketplace theme"""
        marketplace_theme = self.get_object()

        try:
            purchase_result = ThemeMarketplaceService.purchase_theme(
                marketplace_theme=marketplace_theme, user=request.user, store=request.store
            )

            return Response(
                {"message": "Theme purchased successfully", "purchase_details": purchase_result}
            )

        except Exception as e:
            return Response(
                {"error": f"Purchase failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
