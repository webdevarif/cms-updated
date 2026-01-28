"""
URL configuration for translations app.

Routes for dashboard translations endpoints (admin-only).
"""
from django.urls import include, path

app_name = "translations"

urlpatterns = [
    path("dashboard/", include("apps.translations.dashboard.v2.urls")),
]
