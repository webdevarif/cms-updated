"""
URL configuration for search app.

Routes for public, customer, and dashboard search endpoints.
"""
from django.urls import path, include

app_name = 'search'

urlpatterns = [
    path('public/', include('apps.search.public.v2.urls')),
    path('customer/', include('apps.search.customer.v2.urls')),
    path('dashboard/', include('apps.search.dashboard.v2.urls')),
]
