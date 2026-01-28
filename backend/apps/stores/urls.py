"""
URL configuration for stores app.

Routes for public, customer, and dashboard stores endpoints.
"""
from django.urls import include, path

app_name = "stores"

urlpatterns = [
    path("public/", include("apps.stores.public.v2.urls")),
    path("customer/", include("apps.stores.customer.v2.urls")),
    path("dashboard/", include("apps.stores.dashboard.v2.urls")),
]
