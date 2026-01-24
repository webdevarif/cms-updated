"""
URL configuration for cache API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'cache_v2'

router = DefaultRouter()
router.register(r'', views.CacheViewSet, basename='cache')

urlpatterns = [
    path('', include(router.urls)),
]
