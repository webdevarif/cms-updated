"""
URL configuration for forms app.

Routes for public, customer, and dashboard forms endpoints.
"""
from django.urls import include, path

app_name = "forms"

urlpatterns = [
    path("public/", include("apps.forms.public.v2.urls")),
    path("customer/", include("apps.forms.customer.v2.urls")),
    path("dashboard/", include("apps.forms.dashboard.v2.urls")),
]
