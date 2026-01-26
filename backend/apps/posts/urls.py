"""
URL configuration for posts app.

Routes for public, customer, and dashboard posts endpoints.
"""
from django.urls import path, include

app_name = 'posts'

urlpatterns = [
    path('public/', include('apps.posts.public.v2.urls')),
    path('customer/', include('apps.posts.customer.v2.urls')),
    path('dashboard/', include('apps.posts.dashboard.v2.urls')),
]
