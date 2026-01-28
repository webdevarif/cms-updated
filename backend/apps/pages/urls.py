"""
URL configuration for pages app.

Routes for public, customer, and dashboard pages endpoints.
"""
from django.urls import include, path

app_name = "pages"

urlpatterns = [
    path("public/", include("apps.pages.public.v2.urls")),
    path("customer/", include("apps.pages.customer.v2.urls")),
    path("dashboard/", include("apps.pages.dashboard.v2.urls")),
]
