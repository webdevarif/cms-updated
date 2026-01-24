"""
API v2 URL configuration for Digital Farmers CMS.
"""
from django.urls import path, include
from django.contrib import admin

app_name = 'v2'

urlpatterns = [
    # Public APIs (no authentication)
    path('api/public/', include('apps.public.urls')),
    
    # Customer APIs (customer authentication)
    path('api/customer/', include('apps.customer.urls')),
    
    # Dashboard APIs (staff authentication)
    path('api/dashboard/', include('apps.dashboard.urls')),
    
    # Admin
    path('admin/', admin.site.urls),
]
