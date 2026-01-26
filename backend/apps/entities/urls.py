"""
URL configuration for entities app.

Routes for public, customer, and dashboard entities endpoints.
"""
from django.urls import path, include

app_name = 'entities'

urlpatterns = [
    path('public/', include('apps.entities.public.v2.urls')),
    path('customer/', include('apps.entities.customer.v2.urls')),
    path('dashboard/', include('apps.entities.dashboard.v2.urls')),
]
