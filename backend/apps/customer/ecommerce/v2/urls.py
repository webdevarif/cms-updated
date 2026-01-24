"""
URL configuration for customer ecommerce API v2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'customer_ecommerce_v2'

router = DefaultRouter()
router.register(r'cart', views.CustomerCartViewSet, basename='customer_cart')
router.register(r'orders', views.CustomerOrderViewSet, basename='customer_order')

urlpatterns = [
    path('', include(router.urls)),
]
