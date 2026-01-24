"""
URL configuration for forms API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'forms_v2'

router = DefaultRouter()
router.register(r'public', views.PublicFormViewSet, basename='public-forms')
router.register(r'customer', views.CustomerFormViewSet, basename='customer-forms')
router.register(r'dashboard', views.DashboardFormViewSet, basename='dashboard-forms')

urlpatterns = [
    path('', include(router.urls)),
]
