"""
Customer cache API URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CacheCustomerViewSet

router = DefaultRouter()
router.register(r'', CacheCustomerViewSet, basename='cache-customer')

urlpatterns = [
    path('', include(router.urls)),
]
