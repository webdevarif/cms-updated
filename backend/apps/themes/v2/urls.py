"""Themes v2 URL configuration."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ThemePublicViewSet, ThemeDashboardViewSet, TemplatePublicViewSet, TemplateDashboardViewSet

router = DefaultRouter()

# Public endpoints
router.register(r'themes/current', ThemePublicViewSet, basename='theme-current')
router.register(r'templates', TemplatePublicViewSet, basename='template-public')

# Dashboard endpoints
router.register(r'dashboard/themes', ThemeDashboardViewSet, basename='theme-dashboard')
router.register(r'dashboard/templates', TemplateDashboardViewSet, basename='template-dashboard')

urlpatterns = [
    path('api/v2/stores/<int:store_id>/', include(router.urls)),
]
