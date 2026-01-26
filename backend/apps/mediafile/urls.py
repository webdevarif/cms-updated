"""
URL configuration for mediafile app.

Routes for public, customer, and dashboard mediafile endpoints.
"""
from django.urls import path, include

app_name = 'mediafile'

urlpatterns = [
    path('public/', include('apps.mediafile.public.v2.urls')),
    path('customer/', include('apps.mediafile.customer.v2.urls')),
    path('dashboard/', include('apps.mediafile.dashboard.v2.urls')),
]
