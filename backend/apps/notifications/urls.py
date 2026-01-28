"""
URL configuration for notifications app.

Routes for public, customer, and dashboard notification endpoints.
"""
from django.urls import include, path

app_name = "notifications"

urlpatterns = [
    path("public/", include("apps.notifications.public.v2.urls")),
    path("customer/", include("apps.notifications.customer.v2.urls")),
    path("dashboard/", include("apps.notifications.dashboard.v2.urls")),
]
