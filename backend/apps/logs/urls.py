"""
URL configuration for logs app.

Routes for public, customer, and dashboard logs endpoints.
"""
from django.urls import path, include

app_name = 'logs'

urlpatterns = [
    path('public/', include('apps.logs.public.v2.urls')),
    path('customer/', include('apps.logs.customer.v2.urls')),
    path('dashboard/', include('apps.logs.dashboard.v2.urls')),
]
