"""
URL configuration for themes app v2.
"""

from apps.themes.v2.serializers import (
    ColorSchemeSerializer,
    StyleClassSerializer,
    TemplateSerializer,
    ThemeSerializer,
    TypographySerializer,
)
from apps.themes.v2.views import (
    ColorSchemeViewSet,
    LayoutViewSet,
    StyleClassViewSet,
    TemplateViewSet,
    ThemeViewSet,
    TypographyViewSet,
)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# API router for themes
router = DefaultRouter()
router.register(r"themes", ThemeViewSet, basename="theme")
router.register(r"layouts", LayoutViewSet, basename="layout")
router.register(r"color-schemes", ColorSchemeViewSet, basename="color-scheme")
router.register(r"typography", TypographyViewSet, basename="typography")
router.register(r"style-classes", StyleClassViewSet, basename="style-class")
router.register(r"templates", TemplateViewSet, basename="template")

# Additional URL patterns for custom actions
urlpatterns = [
    path(
        "color-schemes/default-schemes/",
        ColorSchemeViewSet.as_view({"get": "default_schemes"}),
        name="color-scheme-default-schemes",
    ),
    path("", include(router.urls)),
]
