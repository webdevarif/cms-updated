"""
Customer Forms API v2 URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for the API
router = DefaultRouter()
router.register(r'forms', views.CustomerFormViewSet, basename='customer-form')
router.register(r'email-templates', views.CustomerEmailTemplateViewSet, basename='customer-email-template')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
