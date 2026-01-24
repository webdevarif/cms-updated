"""
SMTP API v2 URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'smtp'

# Create a router for the API
router = DefaultRouter()

# TODO: Add SMTP v2 viewsets here

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
