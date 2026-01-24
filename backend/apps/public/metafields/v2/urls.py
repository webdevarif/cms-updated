"""
URL configuration for metafields API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'metafields_v2'

router = DefaultRouter()
router.register(r'definitions', views.MetafieldDefinitionViewSet, basename='metafield_definition')
router.register(r'values', views.MetafieldViewSet, basename='metafield')

urlpatterns = [
    path('', include(router.urls)),
]
