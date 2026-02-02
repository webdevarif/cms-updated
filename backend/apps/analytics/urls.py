"""
URL configuration for analytics app.
"""

from django.apps import AppConfig
from django.urls import include, path

app_name = "analytics_v2"

urlpatterns = [
    # Analytics endpoints will be added here
    # For now, we'll just include the main analytics URLs
    path("", include("apps.analytics.v2.urls")),
]
