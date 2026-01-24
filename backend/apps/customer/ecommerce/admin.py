"""
Admin configuration for customer ecommerce.
"""
from django.contrib import admin
from apps.public.ecommerce.models import Cart, Order

admin.site.register(Cart)
admin.site.register(Order)
