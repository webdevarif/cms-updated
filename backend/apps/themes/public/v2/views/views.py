"""
Public themes API views - theme rendering and asset serving.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter

from core.permissions import AllowAnyPublicRead
from apps.themes.models import Theme, Template, Layout, StyleClass, Typography
from apps.themes.services import ThemeRenderingService
from .serializers import (
    ThemePublicSerializer, TemplatePublicSerializer,
    LayoutPublicSerializer, StyleClassPublicSerializer, TypographyPublicSerializer
)


class ThemePublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public theme API - read-only access to active themes and theme assets.
    Provides Liquid-like template rendering for frontend consumption.
    """
    permission_classes = [AllowAnyPublicRead]
    queryset = Theme.objects.filter(is_active=True)
    serializer_class = ThemePublicSerializer

    @extend_schema(
        summary="List themes",
        description="List active themes available for use"
    )
    def list(self, request, *args, **kwargs):
        """List active themes"""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Get theme",
        description="Get theme details and assets"
    )
    def retrieve(self, request, *args, **kwargs):
        """Get theme details"""
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def render_template(self, request, pk=None):
        """
        Render a template using Liquid-like syntax with provided context.
        Used by frontend for dynamic content rendering.
        """
        theme = self.get_object()
        template_slug = request.data.get('template_slug')
        context_data = request.data.get('context', {})

        if not template_slug:
            return Response(
                {'error': 'template_slug is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get template from theme
            template = Template.objects.filter(
                theme=theme,
                slug=template_slug,
                is_active=True
            ).first()

            if not template:
                return Response(
                    {'error': 'Template not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Render template with context
            rendered_html = ThemeRenderingService.render_template(
                template=template,
                context=context_data,
                store=request.store if hasattr(request, 'store') else None
            )

            return Response({
                'rendered_html': rendered_html,
                'template_slug': template_slug,
                'theme': theme.slug
            })

        except Exception as e:
            return Response(
                {'error': f'Rendering failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def assets(self, request, pk=None):
        """
        Get all theme assets (CSS, JS, images) for frontend consumption.
        """
        theme = self.get_object()

        try:
            assets = ThemeRenderingService.get_theme_assets(theme)
            return Response(assets)

        except Exception as e:
            return Response(
                {'error': f'Asset retrieval failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def render_page(self, request, pk=None):
        """
        Render a complete page using theme layout and content.
        """
        theme = self.get_object()
        page_data = request.data.get('page_data', {})

        if not page_data:
            return Response(
                {'error': 'page_data is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            rendered_page = ThemeRenderingService.render_page(
                theme=theme,
                page_data=page_data,
                store=request.store if hasattr(request, 'store') else None,
                request=request
            )

            return Response({
                'rendered_html': rendered_page['html'],
                'css_files': rendered_page['css_files'],
                'js_files': rendered_page['js_files'],
                'meta_tags': rendered_page['meta_tags']
            })

        except Exception as e:
            return Response(
                {'error': f'Page rendering failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TemplatePublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public template API - read-only access to theme templates.
    """
    permission_classes = [AllowAnyPublicRead]
    serializer_class = TemplatePublicSerializer

    def get_queryset(self):
        return Template.objects.filter(
            theme__is_active=True,
            is_active=True
        ).select_related('theme')


class LayoutPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public layout API - read-only access to theme layouts.
    """
    permission_classes = [AllowAnyPublicRead]
    serializer_class = LayoutPublicSerializer

    def get_queryset(self):
        return Layout.objects.filter(
            theme__is_active=True,
            is_active=True
        ).select_related('theme')


class StyleClassPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public style class API - read-only access to theme CSS classes.
    """
    permission_classes = [AllowAnyPublicRead]
    serializer_class = StyleClassPublicSerializer

    def get_queryset(self):
        return StyleClass.objects.filter(
            theme__is_active=True,
            is_active=True
        ).select_related('theme')


class TypographyPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public typography API - read-only access to theme typography settings.
    """
    permission_classes = [AllowAnyPublicRead]
    serializer_class = TypographyPublicSerializer

    def get_queryset(self):
        return Typography.objects.filter(
            theme__is_active=True,
            is_active=True
        ).select_related('theme')
