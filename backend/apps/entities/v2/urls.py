"""
URL configuration for entities API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'entities_v2'

router = DefaultRouter()
router.register(r'', views.EntityViewSet, basename='entity')

urlpatterns = [
    path('', include(router.urls)),
]
