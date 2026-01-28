"""
URL configuration for metafields app.

Routes for public, customer, and dashboard metafields endpoints.
"""
from django.urls import include, path

app_name = "metafields"

urlpatterns = [
    path("public/", include("apps.metafields.public.v2.urls")),
    path("customer/", include("apps.metafields.customer.v2.urls")),
    path("dashboard/", include("apps.metafields.dashboard.v2.urls")),
]
