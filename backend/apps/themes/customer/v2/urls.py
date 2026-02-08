"""
Customer themes API URLs.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import ThemeCustomerViewSet

router = DefaultRouter()
router.register(r"", ThemeCustomerViewSet, basename="theme-customer")

urlpatterns = [
    path("", include(router.urls)),
]
