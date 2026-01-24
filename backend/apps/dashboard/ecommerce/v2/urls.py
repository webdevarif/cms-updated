"""
URL configuration for dashboard ecommerce API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'dashboard_ecommerce_v2'

router = DefaultRouter()
router.register(r'products', views.DashboardProductViewSet, basename='dashboard_product')
router.register(r'orders', views.DashboardOrderViewSet, basename='dashboard_order')

urlpatterns = [
    path('', include(router.urls)),
]
