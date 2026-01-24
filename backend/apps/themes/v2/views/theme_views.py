"""Theme views."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.viewsets import StoreScopedViewSet


class ThemePublicViewSet(viewsets.ReadOnlyModelViewSet):
    """Public theme API"""
    
    queryset = None
    serializer_class = None
    
    def get_queryset(self):
        """Get active theme for store"""
        store_id = self.kwargs.get('store_id') or getattr(self.request, 'store_id', None)
        if not store_id:
            return Theme.objects.none()
        from ..models import Theme
        return Theme.objects.filter(store_id=store_id, is_active=True)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current active theme"""
        from ..models import Theme
        store_id = self.kwargs.get('store_id')
        theme = Theme.objects.filter(store_id=store_id, is_active=True).first()
        
        if not theme:
            return Response({'error': 'No active theme found'}, status=status.HTTP_404_NOT_FOUND)
        
        from ..v2.serializers import ThemePublicSerializer
        serializer = ThemePublicSerializer(theme)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def scheme(self, request):
        """Get active color scheme"""
        from ..models import Theme
        store_id = self.kwargs.get('store_id')
        theme = Theme.objects.filter(store_id=store_id, is_active=True).first()
        
        if not theme:
            return Response({'error': 'No active theme found'}, status=status.HTTP_404_NOT_FOUND)
        
        color_scheme = theme.get_active_color_scheme()
        if not color_scheme:
            return Response({'error': 'No color scheme found'}, status=status.HTTP_404_NOT_FOUND)
        
        from ..v2.serializers import ColorSchemePublicSerializer
        serializer = ColorSchemePublicSerializer(color_scheme)
        return Response(serializer.data)


class ThemeDashboardViewSet(StoreScopedViewSet):
    """Dashboard theme management API"""
    
    def get_queryset(self):
        """Filter by current store"""
        from ..models import Theme
        return Theme.objects.filter(store=self.request.user.stores.first())
    
    def get_serializer_class(self):
        """Get appropriate serializer"""
        from ..v2.serializers import ThemeSerializer, ThemeCreateSerializer
        if self.action in ['create']:
            return ThemeCreateSerializer
        return ThemeSerializer
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate theme"""
        theme = self.get_object()
        theme.activate()
        from ..v2.serializers import ThemeSerializer
        serializer = ThemeSerializer(theme)
        return Response(serializer.data)
