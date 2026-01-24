"""
URL configuration for dashboard API endpoints.
"""
from django.urls import path, include

app_name = 'dashboard'

# API v2 endpoints
urlpatterns = [
    # Forms API v2
    path('v2/forms/', include('apps.dashboard.forms.v2.urls')),
    
    # Metafields API v2
    path('v2/metafields/', include('apps.dashboard.metafields.v2.urls')),
    
    # Add other v2 API endpoints here
]
