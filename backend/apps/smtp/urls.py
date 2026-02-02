"""
URL configuration for smtp app.

Routes for public, customer, and dashboard smtp endpoints.
"""

from django.urls import include, path

app_name = "smtp"

urlpatterns = [
    path("public/", include("apps.smtp.public.v1.urls")),
    path("customer/", include("apps.smtp.customer.v1.urls")),
    path("dashboard/", include("apps.smtp.dashboard.v1.urls")),
]
