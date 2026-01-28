"""
URL configuration for mediafile customer API v2.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MediafileCustomerViewSet, MediafolderCustomerViewSet

# Customer router
router = DefaultRouter()
router.register(r"files", MediafileCustomerViewSet, basename="customer-mediafiles")
router.register(r"folders", MediafolderCustomerViewSet, basename="customer-mediafolders")

urlpatterns = [
    path("", include(router.urls)),
]
