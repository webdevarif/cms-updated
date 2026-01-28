"""
URL configuration for giftcards app.

Routes for public, customer, and dashboard giftcards endpoints.
"""
from django.urls import include, path

app_name = "giftcards"

urlpatterns = [
    path("public/", include("apps.giftcards.public.v2.urls")),
    path("customer/", include("apps.giftcards.customer.v2.urls")),
    path("dashboard/", include("apps.giftcards.dashboard.v2.urls")),
]
