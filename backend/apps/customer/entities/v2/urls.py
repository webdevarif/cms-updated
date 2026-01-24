"""
URLs for customer entities API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomerEntityViewSet

router = DefaultRouter()
router.register(r'', CustomerEntityViewSet, basename='customer-entity')

urlpatterns = [
    path('v2/api/customer/entities/', include(router.urls)),
]
