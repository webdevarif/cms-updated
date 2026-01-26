"""
URL configuration for public API endpoints.
"""
from django.urls import path, include

app_name = 'public'

urlpatterns = [
    # Forms API
    path('forms/', include('apps.public.forms.v2.urls')),
    
    # Gift Cards API
    # path('gift-cards/', include('apps.public.giftcards.v2.urls')),
    
    # Logs API
    path('logs/', include('apps.logs.v2.urls')),
    
    # Other public APIs will be added here
]
