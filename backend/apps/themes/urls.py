"""
URL configuration for themes app.

Routes for public, customer, and dashboard themes endpoints.
"""
from django.urls import include, path

app_name = "themes"

urlpatterns = [
    path("public/", include("apps.themes.public.v2.urls")),
    path("customer/", include("apps.themes.customer.v2.urls")),
    path("dashboard/", include("apps.themes.dashboard.v2.urls")),
]
