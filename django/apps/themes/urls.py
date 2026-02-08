"""
URL configuration for themes app.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from . import views

app_name = "themes"

router = DefaultRouter()
router.register("list", views.ThemeViewSet, basename="theme")
router.register("color-schemes", views.ColorSchemeViewSet, basename="color-scheme")
router.register("layouts", views.LayoutViewSet, basename="layout")
router.register("style-classes", views.StyleClassViewSet, basename="style-class")
router.register("templates", views.TemplateViewSet, basename="template")

urlpatterns = [
    path("", include(router.urls)),
]
