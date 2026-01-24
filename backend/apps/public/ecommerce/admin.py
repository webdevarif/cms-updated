"""
Admin configuration for ecommerce.
"""
from django.contrib import admin
from .models import Product, ProductVariant, Cart, CartItem, Order, OrderItem
from .models.customers import Customer, Collection, Coupon
from .models.inventory import Inventory, InventoryTransaction, PaymentMethod, Payment
from .models.products import ProductCategory, ProductTag, TaxClass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin for Product"""
    list_display = ['title', 'sku', 'status', 'is_available', 'store']
    list_filter = ['status', 'is_available', 'is_featured']
    search_fields = ['title', 'sku']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Admin for ProductVariant"""
    list_display = ['product', 'title', 'sku', 'inventory_quantity']
    list_filter = ['is_available']


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    """Admin for ProductCategory"""
    list_display = ['name', 'slug', 'is_active', 'store']


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    """Admin for ProductTag"""
    list_display = ['name', 'store']


@admin.register(TaxClass)
class TaxClassAdmin(admin.ModelAdmin):
    """Admin for TaxClass"""
    list_display = ['name', 'rate', 'store']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin for Cart"""
    list_display = ['id', 'user', 'session_key', 'store']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for Order"""
    list_display = ['order_number', 'customer_email', 'status', 'total', 'store']
    list_filter = ['status']
    search_fields = ['order_number', 'customer_email']
    readonly_fields = ['created_at', 'updated_at', 'shipped_at', 'delivered_at']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin for Customer"""
    list_display = ['user', 'store', 'first_name', 'last_name']


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    """Admin for Collection"""
    list_display = ['name', 'slug', 'store']
    search_fields = ['name']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Admin for Coupon"""
    list_display = ['code', 'discount_type', 'discount_value', 'is_active']
    list_filter = ['discount_type', 'is_active']


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    """Admin for Inventory"""
    list_display = ['product', 'quantity']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """Admin for PaymentMethod"""
    list_display = ['name', 'provider', 'is_active']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin for Payment"""
    list_display = ['order', 'amount', 'status', 'created_at']
    list_filter = ['status']
