"""
URL configuration for stores API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'stores_v2'

router = DefaultRouter()
router.register(r'public', views.StorePublicViewSet, basename='store-public')
router.register(r'', views.StoreViewSet, basename='store')

urlpatterns = [
    path('', include(router.urls)),
]
