"""
Dashboard translations API URLs.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TranslationDashboardViewSet

router = DefaultRouter()
router.register(r"translations", TranslationDashboardViewSet, basename="dashboard-translations")

urlpatterns = [
    path("", include(router.urls)),
]
