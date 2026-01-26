"""
Customer pages URLs - authenticated user manages own pages.
Architectural + real implementation for customer pages interface.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PageCustomerViewSet

router = DefaultRouter()
router.register(r'pages', PageCustomerViewSet, basename='customer-pages')

urlpatterns = [
    path('', include(router.urls)),
]
