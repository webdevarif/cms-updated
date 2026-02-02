"""
URL configuration for accounts app.

Routes for public, customer, and dashboard accounts endpoints.
"""

from django.urls import include, path

app_name = "accounts"

urlpatterns = [
    path("public/", include("apps.accounts.public.v2.urls")),
    path("customer/", include("apps.accounts.customer.v2.urls")),
    path("dashboard/", include("apps.accounts.dashboard.v2.urls")),
]
