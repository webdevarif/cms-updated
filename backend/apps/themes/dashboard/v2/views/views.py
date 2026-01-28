"""
Dashboard themes API views - full admin interface for theme management.
"""
from apps.themes.models import Theme
from apps.themes.services import ThemeService
from core.permissions import IsStoreAdmin
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..serializers.serializers import ThemeDashboardSerializer


class ThemeDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard theme API - store admins can fully manage themes.
    """

    permission_classes = [IsStoreAdmin]
    serializer_class = ThemeDashboardSerializer

    def get_queryset(self):
        """Return all themes for admin management"""
        return Theme.objects.all().select_related("created_by")

    @extend_schema(summary="List themes", description="List all themes for admin management")
    def list(self, request, *args, **kwargs):
        """List themes"""
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Get theme", description="Get theme details")
    def retrieve(self, request, *args, **kwargs):
        """Get theme details"""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Create theme", description="Create new theme")
    def create(self, request, *args, **kwargs):
        """Create theme"""
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Update theme", description="Update theme details")
    def update(self, request, *args, **kwargs):
        """Update theme"""
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Delete theme", description="Delete theme")
    def destroy(self, request, *args, **kwargs):
        """Delete theme"""
        return super().destroy(request, *args, **kwargs)
