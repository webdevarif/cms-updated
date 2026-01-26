"""
Public themes API.
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from apps.themes.models import Theme
from .serializers import ThemePublicSerializer, ColorSchemePublicSerializer, TemplatePublicSerializer
from apps.themes.v2.services import ThemeService


class ThemePublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public theme API - no authentication required.
    Provides read-only access to active themes for asset retrieval.
    """
    permission_classes = [AllowAny]
    queryset = Theme.objects.filter(is_active=True)
    serializer_class = ThemePublicSerializer
    
    def get_queryset(self):
        """Filter by store if provided"""
        store_id = self.kwargs.get('store_id') or getattr(self.request, 'store_id', None)
        if not store_id:
            return Theme.objects.none()
        
        return Theme.objects.filter(store_id=store_id, is_active=True)
    
    @extend_schema(
        summary="Get current theme",
        description="Get current active theme for store",
        tags=["Themes Public"]
    )
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current active theme"""
        store_id = self.kwargs.get('store_id') or getattr(self.request, 'store_id', None)
        theme = Theme.objects.filter(store_id=store_id, is_active=True).first()
        
        if not theme:
            return Response({'error': 'No active theme found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ThemePublicSerializer(theme)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get theme assets",
        description="Get theme CSS/JS assets"
    )
    @action(detail=True, methods=['get'])
    def assets(self, request, pk=None):
        """Get theme assets"""
        theme = self.get_object()
        assets = ThemeService.get_theme_assets(theme)
        
        return Response(assets)
    
    @extend_schema(
        summary="Get color scheme",
        description="Get active color scheme"
    )
    @action(detail=True, methods=['get'])
    def color_scheme(self, request, pk=None):
        """Get active color scheme"""
        store_id = self.kwargs.get('store_id') or getattr(self.request, 'store_id', None)
        theme = Theme.objects.filter(store_id=store_id, is_active=True).first()
        
        if not theme:
            return Response({'error': 'No active theme found'}, status=status.HTTP_404_NOT_FOUND)
        
        color_scheme = theme.get_active_color_scheme()
        if not color_scheme:
            return Response({'error': 'No color scheme found'}, status=status.HTTP_404_NOT_FOUND)
        
        from apps.themes.v2.serializers.color_scheme_serializers import ColorSchemePublicSerializer
        serializer = ColorSchemePublicSerializer(color_scheme)
        return Response(serializer.data)
