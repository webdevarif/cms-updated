"""
URL configuration for webhooks app.

Routes for public, customer, and dashboard webhook endpoints.
"""
from django.urls import path, include

app_name = 'webhooks'

urlpatterns = [
    path('public/', include('apps.webhooks.public.v2.urls')),
    path('customer/', include('apps.webhooks.customer.v2.urls')),
    path('dashboard/', include('apps.webhooks.dashboard.v2.urls')),
]
