"""
URL configuration for ecommerce app.

Routes for public, customer, and dashboard ecommerce endpoints.
"""
from django.urls import path, include

app_name = 'ecommerce'

urlpatterns = [
    path('public/', include('apps.ecommerce.public.v2.urls')),
    path('customer/', include('apps.ecommerce.customer.v2.urls')),
    path('dashboard/', include('apps.ecommerce.dashboard.v2.urls')),
]
