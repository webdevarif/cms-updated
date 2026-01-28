"""
Public themes API views - theme rendering and asset serving.
"""
from apps.themes.models import Theme
from apps.themes.services import ThemeService
from core.permissions import AllowAnyPublicRead
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..serializers.serializers import ThemePublicSerializer


class ThemePublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public theme API - read-only access to active themes and theme assets.
    """

    permission_classes = [AllowAny]
    queryset = Theme.objects.filter(is_active=True)
    serializer_class = ThemePublicSerializer

    @extend_schema(summary="List themes", description="List active themes available for use")
    def list(self, request, *args, **kwargs):
        """List active themes"""
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Get theme", description="Get theme details and assets")
    def retrieve(self, request, *args, **kwargs):
        """Get theme details"""
        return super().retrieve(request, *args, **kwargs)
