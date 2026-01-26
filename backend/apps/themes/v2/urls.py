"""
URL configuration for themes app v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.themes.v2.views import ThemeViewSet, ColorSchemeViewSet, TypographyViewSet, StyleClassViewSet, TemplateViewSet

# API router for themes
router = DefaultRouter()
router.register(r'themes', ThemeViewSet, basename='theme')
router.register(r'color-schemes', ColorSchemeViewSet, basename='color-scheme')
router.register(r'typography', TypographyViewSet, basename='typography')
router.register(r'style-classes', StyleClassViewSet, basename='style-class')
router.register(r'templates', TemplateViewSet, basename='template')

urlpatterns = [
    path('', include(router.urls)),
]
