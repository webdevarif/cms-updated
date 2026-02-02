"""
URL configuration for notifications app.

Routes for customer and dashboard notification endpoints.
Public notifications API has been removed as it was unused.
"""

from django.urls import include, path

app_name = "notifications"

urlpatterns = [
    # Public notifications API removed - was unused and deprecated
    path("customer/", include("apps.notifications.customer.v2.urls")),
    path("dashboard/", include("apps.notifications.dashboard.v2.urls")),
]
