"""
URL configuration for forms dashboard API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DashboardFormTemplateViewSet, DashboardFormSubmissionViewSet

# Dashboard router
router = DefaultRouter()
router.register(r'forms', DashboardFormTemplateViewSet, basename='dashboard-forms')
router.register(r'submissions', DashboardFormSubmissionViewSet, basename='dashboard-submissions')

urlpatterns = [
    path('', include(router.urls)),
]
