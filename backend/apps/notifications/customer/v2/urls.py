"""
Customer notification URLs.
"""

from rest_framework.routers import DefaultRouter

from django.urls import include, path

from . import views

customer_router = DefaultRouter()
customer_router.register(
    r"notifications",
    views.NotificationCustomerViewSet,
    basename="notification-customer",
)
customer_router.register(
    r"preferences",
    views.NotificationPreferenceCustomerViewSet,
    basename="preference-customer",
)

urlpatterns = [
    path("", include(customer_router.urls)),
]
