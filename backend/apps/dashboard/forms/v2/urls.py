"""
Dashboard Forms API v2 URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for the API
router = DefaultRouter()
router.register(r'forms', views.DashboardFormTemplateViewSet, basename='dashboard-form')
router.register(r'submissions', views.DashboardFormSubmissionViewSet, basename='dashboard-form-submission')
router.register(r'email-templates', views.DashboardEmailTemplateViewSet, basename='dashboard-email-template')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
