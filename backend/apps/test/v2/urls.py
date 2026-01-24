"""
URL configuration for test API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'test_v2'

router = DefaultRouter()
router.register(r'runs', views.TestRunViewSet, basename='test_run')

urlpatterns = [
    path('', include(router.urls)),
]
