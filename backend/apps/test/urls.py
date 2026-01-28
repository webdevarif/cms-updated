"""
URL configuration for test app.

Routes for public test endpoints.
"""
from django.urls import include, path

app_name = "test"

urlpatterns = [
    path("v2/", include("apps.test.public.v2.urls")),
]
