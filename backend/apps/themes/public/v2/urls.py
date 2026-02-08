"""
Public themes API URLs.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import ThemePublicViewSet

router = DefaultRouter()
router.register(r"", ThemePublicViewSet, basename="theme-public")

urlpatterns = [
    path("", include(router.urls)),
]
