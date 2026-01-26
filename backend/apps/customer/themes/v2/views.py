"""
Customer themes API.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.themes.models import Theme, Template
from .serializers import ThemeCustomerSerializer, TemplateCustomerSerializer
from apps.themes.v2.services import ThemeService


class ThemeCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer theme endpoints for authenticated users.
    Users can preview and customize their own themes.
    """
    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = ThemeCustomerSerializer
    
    def get_queryset(self):
        """Filter by current user's store"""
        return Theme.objects.filter(store=self.request.store)
    
    @extend_schema(
        summary="Get current theme",
        description="Get current active theme for store"
    )
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current active theme"""
        theme = Theme.objects.filter(store=self.request.store, is_active=True).first()
        
        if not theme:
            return Response({'error': 'No active theme found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ThemeSerializer(theme)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Preview theme",
        description="Preview theme with sample data"
    )
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """Preview theme"""
        theme = self.get_object()
        preview_data = ThemeService.preview_theme(theme, request.user)
        
        return Response(preview_data)
    
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


class TemplateCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer template endpoints for authenticated users.
    Users can view templates and preview them.
    """
    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = TemplateCustomerSerializer
    
    def get_queryset(self):
        """Get templates for current user's store"""
        template_role = self.request.query_params.get('role', None)
        from apps.themes.models import Template
        queryset = Template.objects.filter(
            store=self.request.store,
            is_active=True
        )
        
        if template_role:
            queryset = queryset.filter(template_role=template_role)
        
        return queryset
    
    @extend_schema(
        summary="Get templates by role",
        description="Get templates by role"
    )
    @action(detail=False, methods=['get'])
    def by_role(self, request):
        """Get templates by role"""
        template_role = self.request.query_params.get('role', 'body')
        from apps.themes.models import Template
        
        templates = Template.objects.filter(
            store=self.request.store,
            template_role=template_role,
            is_active=True
        )
        
        serializer = TemplatePublicSerializer(templates, many=True)
        return Response(serializer.data)
