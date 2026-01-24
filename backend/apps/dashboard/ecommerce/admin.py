"""
Admin configuration for dashboard ecommerce.
"""
from django.contrib import admin
from apps.public.ecommerce.models import Product, Order, Cart

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Cart)
