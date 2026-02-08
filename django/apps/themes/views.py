from apps.stores.utils import StoreScopedMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ColorScheme, Layout, StyleClass, Template, Theme
from .serializers import (
    ColorSchemeSerializer,
    LayoutSerializer,
    StyleClassSerializer,
    TemplateSerializer,
    ThemeSerializer,
)


class ThemeViewSet(StoreScopedMixin, viewsets.ModelViewSet):
    """
    ViewSet for Theme model with store scoping.
    """

    serializer_class = ThemeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_default", "key"]
    search_fields = ["name", "key", "description"]
    ordering = ["-is_default", "name"]

    def get_queryset(self):
        """
        Filter themes by store.
        """
        return Theme.objects.filter(store=self.store).prefetch_related(
            "color_schemes", "layouts", "style_classes", "templates"
        )

    def perform_create(self, serializer):
        """
        Create theme for the specified store.
        """
        serializer.save(store=self.store)

    def perform_destroy(self, instance):
        """
        Prevent deletion if this is the only theme for the store.
        """
        theme_count = Theme.objects.filter(store=self.store).count()
        if theme_count <= 1:
            raise ValidationError(
                {
                    "error": "Cannot delete the last theme for this store. At least one theme must exist."
                }
            )
        super().perform_destroy(instance)


class ColorSchemeViewSet(StoreScopedMixin, viewsets.ModelViewSet):
    """
    ViewSet for ColorScheme model with theme/store scoping.
    """

    serializer_class = ColorSchemeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["theme", "is_default", "key"]
    search_fields = ["name", "key"]
    ordering = ["-is_default", "name"]

    def get_queryset(self):
        """
        Filter color schemes by store.
        """
        return ColorScheme.objects.filter(theme__store=self.store)

    def perform_create(self, serializer):
        """
        Create color scheme for a theme in the specified store.
        """
        theme_id = self.request.data.get("theme")
        if theme_id:
            theme = Theme.objects.get(pk=theme_id)
            # Verify theme belongs to the store
            if theme.store != self.store:
                raise ValidationError({"theme": "Theme does not belong to this store."})
        serializer.save()


class LayoutViewSet(StoreScopedMixin, viewsets.ModelViewSet):
    """
    ViewSet for Layout model with theme/store scoping.
    """

    serializer_class = LayoutSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["theme", "key"]
    search_fields = ["name", "key"]
    ordering = ["name"]

    def get_queryset(self):
        """
        Filter layouts by store.
        """
        return Layout.objects.filter(theme__store=self.store)

    def perform_create(self, serializer):
        """
        Create layout for a theme in the specified store.
        """
        serializer.save(store=self.store)


class StyleClassViewSet(StoreScopedMixin, viewsets.ModelViewSet):
    """
    ViewSet for StyleClass model with theme/store scoping.
    """

    serializer_class = StyleClassSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["theme", "key"]
    search_fields = ["name", "key", "css_class"]
    ordering = ["name"]

    def get_queryset(self):
        """
        Filter style classes by store.
        """
        if not hasattr(self, "store") or not self.store:
            return StyleClass.objects.none()
        return StyleClass.objects.filter(theme__store=self.store)

    def perform_create(self, serializer):
        """
        Create style class for a theme in the specified store.
        """
        theme_id = self.request.data.get("theme")
        if theme_id:
            theme = Theme.objects.get(pk=theme_id)
            # Verify theme belongs to the store
            if theme.store != self.store:
                raise ValidationError({"theme": "Theme does not belong to this store."})
        serializer.save()


class TemplateViewSet(StoreScopedMixin, viewsets.ModelViewSet):
    """
    ViewSet for Template model with theme/store scoping.
    """

    serializer_class = TemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["theme", "key"]
    search_fields = ["name", "key"]
    ordering = ["name"]

    def get_queryset(self):
        """
        Filter templates by store.
        """
        return Template.objects.filter(theme__store=self.store)

    def perform_create(self, serializer):
        """
        Create template for a theme in the specified store.
        """
        theme_id = self.request.data.get("theme")
        if theme_id:
            theme = Theme.objects.get(pk=theme_id)
            # Verify theme belongs to the store
            if theme.store != self.store:
                raise ValidationError({"theme": "Theme does not belong to this store."})
        serializer.save()
