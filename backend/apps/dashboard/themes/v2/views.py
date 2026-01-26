"""
Dashboard themes API.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from core.permissions import IsStoreOwner
from apps.themes.models import Theme, Template
from apps.themes.v2.serializers.theme_serializers import ThemeSerializer, ThemeCreateSerializer
from apps.themes.v2.serializers.template_serializers import TemplateSerializer, TemplateCreateSerializer
from apps.themes.v2.services import ThemeService


class ThemeDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard theme management endpoints for store owners and admins.
    Provides full CRUD access to themes with management actions.
    """
    permission_classes = [IsStoreOwner]
    serializer_class = ThemeSerializer
    
    def get_queryset(self):
        """Filter by current user's stores"""
        return Theme.objects.filter(store=self.request.store)
    
    @extend_schema(
        summary="Create theme",
        description="Create new theme",
        request=ThemeCreateSerializer,
        responses={201: ThemeSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Create new theme"""
        serializer = ThemeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        theme = ThemeService.create_theme(
            store=request.store,
            name=serializer.validated_data['name'],
            user=request.user
        )
        
        return Response(
            ThemeSerializer(theme).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Activate theme",
        description="Activate a theme"
    )
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate theme"""
        theme = self.get_object()
        ThemeService.activate_theme(theme, request.user)
        
        return Response({
            'status': 'activated',
            'message': f'Theme {theme.name} has been activated'
        })
    
    @extend_schema(
        summary="Deactivate theme",
        description="Deactivate a theme"
    )
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate theme"""
        theme = self.get_object()
        ThemeService.deactivate_theme(theme, request.user)
        
        return Response({
            'status': 'deactivated',
            'message': f'Theme {theme.name} has been deactivated'
        })
    
    @extend_schema(
        summary="Duplicate theme",
        description="Duplicate a theme"
    )
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate theme"""
        theme = self.get_object()
        new_theme = ThemeService.duplicate_theme(theme, request.user)
        
        return Response(
            ThemeSerializer(new_theme).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Theme analytics",
        description="Get theme usage analytics"
    )
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get theme analytics"""
        theme = self.get_object()
        days = int(request.GET.get('days', 30))
        
        analytics = ThemeService.get_theme_analytics(theme, days)
        return Response(analytics)


class TemplateDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard template management endpoints for store owners and admins.
    Provides full CRUD access to templates.
    """
    permission_classes = [IsStoreOwner]
    serializer_class = TemplateSerializer
    
    def get_queryset(self):
        """Filter by current store"""
        return Template.objects.filter(store=self.request.store)
    
    @extend_schema(
        summary="Create template",
        description="Create new template",
        request=TemplateCreateSerializer,
        responses={201: TemplateSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Create new template"""
        serializer = TemplateCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        template = TemplateService.create_template(
            store=self.request.store,
            **serializer.validated_data
        )
        
        return Response(
            TemplateSerializer(template).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Duplicate template",
        description="Duplicate a template"
    )
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate template"""
        template = self.get_object()
        new_template = TemplateService.duplicate_template(template, request.user)
        
        return Response(
            TemplateSerializer(new_template).data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Set as default",
        description="Set template as default for its role"
    )
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set template as default"""
        template = self.get_object()
        TemplateService.set_as_default(template, request.user)
        
        return Response({
            'status': 'success',
            'message': f'Template {template.name} is now default for {template.template_role}'
        })
    
    @extend_schema(
        summary="Preview template",
        description="Preview template with sample data"
    )
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """Preview template"""
        template = self.get_object()
        preview_data = TemplateService.preview_template(template, request.user)
        
        return Response(preview_data)
