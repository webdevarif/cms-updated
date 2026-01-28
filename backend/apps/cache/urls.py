"""
URL configuration for cache app.

Routes for public, customer, and dashboard cache endpoints.
"""
from django.urls import include, path

app_name = "cache"

urlpatterns = [
    path("public/", include("apps.cache.public.v2.urls")),
    path("customer/", include("apps.cache.customer.v2.urls")),
    path("dashboard/", include("apps.cache.dashboard.v2.urls")),
]
