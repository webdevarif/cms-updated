"""
API views for themes app v2.
"""
from apps.themes.models import ColorScheme, StyleClass, Template, Theme, Typography
from apps.themes.services.theme_service import ThemeService
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class ThemeViewSet(viewsets.ModelViewSet):
    """
    Theme management API endpoints.
    """

    queryset = Theme.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["store", "is_active"]

    def get_queryset(self):
        """Filter by store if provided"""
        queryset = super().get_queryset()
        store_id = self.request.query_params.get("store")
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        return queryset

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate this theme"""
        theme = self.get_object()
        theme.activate()
        return Response({"status": "activated"})

    @action(detail=True, methods=["get"])
    def settings(self, request, pk=None):
        """Get all theme settings"""
        theme = self.get_object()
        settings = ThemeService.get_theme_settings(theme)
        return Response(settings)


class ColorSchemeViewSet(viewsets.ModelViewSet):
    """
    Color scheme management API endpoints.
    """

    queryset = ColorScheme.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["theme", "is_default"]

    def get_queryset(self):
        """Filter by theme if provided"""
        queryset = super().get_queryset()
        theme_id = self.request.query_params.get("theme")
        if theme_id:
            queryset = queryset.filter(theme_id=theme_id)
        return queryset

    @action(detail=True, methods=["post"])
    def set_default(self, request, pk=None):
        """Set this color scheme as default"""
        color_scheme = self.get_object()
        # Remove default from other schemes
        ColorScheme.objects.filter(theme=color_scheme.theme).update(is_default=False)
        color_scheme.is_default = True
        color_scheme.save()
        return Response({"status": "set as default"})


class TypographyViewSet(viewsets.ModelViewSet):
    """
    Typography management API endpoints.
    """

    queryset = Typography.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["theme"]

    def get_queryset(self):
        """Filter by theme if provided"""
        queryset = super().get_queryset()
        theme_id = self.request.query_params.get("theme")
        if theme_id:
            queryset = queryset.filter(theme_id=theme_id)
        return queryset


class StyleClassViewSet(viewsets.ModelViewSet):
    """
    Style class management API endpoints.
    """

    queryset = StyleClass.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["theme"]

    def get_queryset(self):
        """Filter by theme if provided"""
        queryset = super().get_queryset()
        theme_id = self.request.query_params.get("theme")
        if theme_id:
            queryset = queryset.filter(theme_id=theme_id)
        return queryset

    @action(detail=True, methods=["get"])
    def css(self, request, pk=None):
        """Get CSS for specific mode"""
        style_class = self.get_object()
        mode = request.query_params.get("mode", "light")
        css = style_class.get_css(mode)
        return Response(css)


class TemplateViewSet(viewsets.ModelViewSet):
    """
    Template management API endpoints.
    """

    queryset = Template.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["theme", "template_role", "is_active"]

    def get_queryset(self):
        """Filter by theme if provided"""
        queryset = super().get_queryset()
        theme_id = self.request.query_params.get("theme")
        if theme_id:
            queryset = queryset.filter(theme_id=theme_id)
        return queryset

    @action(detail=True, methods=["post"])
    def render(self, request, pk=None):
        """Render template with context"""
        template = self.get_object()
        context = request.data.get("context", {})
        rendered = template.render(context)
        return Response({"rendered": rendered})
