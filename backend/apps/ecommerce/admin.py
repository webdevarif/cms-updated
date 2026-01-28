"""
Admin configuration for ecommerce app.
"""
from django.contrib import admin

from .models import (
    Cart,
    CartItem,
    Coupon,
    CouponCampaign,
    CustomerProfile,
    Inventory,
    Order,
    OrderItem,
    Payment,
    PaymentMethod,
    Product,
    ProductCategory,
    ProductCollection,
    ProductVariant,
)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "store", "parent", "is_active", "position", "created_at"]
    list_filter = ["is_active", "created_at", "store"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]
    prepopulated_fields = {"slug": ("name",)}
    date_hierarchy = "created_at"
    raw_id_fields = ["store", "parent"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["title", "store", "category", "price", "status", "is_featured", "created_at"]
    list_filter = ["status", "is_featured", "created_at", "store", "category"]
    search_fields = ["title", "sku", "description"]
    readonly_fields = ["created_at", "updated_at"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    raw_id_fields = ["store", "category", "created_by"]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ["title", "product", "sku", "quantity", "position"]
    list_filter = ["product"]
    search_fields = ["title", "sku"]
    raw_id_fields = ["product"]


@admin.register(ProductCollection)
class ProductCollectionAdmin(admin.ModelAdmin):
    list_display = ["title", "store", "is_featured", "position", "created_at"]
    list_filter = ["is_featured", "created_at", "store"]
    search_fields = ["title", "description"]
    readonly_fields = ["created_at", "updated_at"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    raw_id_fields = ["store", "created_by"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "store", "user", "session_key", "created_at"]
    list_filter = ["created_at", "store"]
    search_fields = ["user__email", "session_key"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    raw_id_fields = ["store", "user"]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["cart", "product", "quantity", "price", "line_total", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["product__title"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    raw_id_fields = ["cart", "product", "variant"]


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "store", "phone", "total_orders", "total_spent", "created_at"]
    list_filter = ["created_at", "gender", "marketing_consent", "store"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "phone"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    raw_id_fields = ["user", "store"]


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ["product", "quantity", "reserved_quantity", "updated_at"]
    list_filter = ["updated_at"]
    search_fields = ["product__title"]
    readonly_fields = ["updated_at"]
    raw_id_fields = ["product"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "customer", "store", "status", "total_amount", "created_at"]
    list_filter = ["status", "created_at", "store"]
    search_fields = ["order_number", "customer_email", "customer_phone"]
    readonly_fields = ["created_at", "updated_at", "confirmed_at", "shipped_at", "delivered_at"]
    date_hierarchy = "created_at"
    raw_id_fields = ["store", "customer"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        "order",
        "product",
        "product_sku",
        "quantity",
        "unit_price",
        "total_price",
        "created_at",
    ]
    list_filter = ["created_at"]
    search_fields = ["product__title", "product_sku"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    raw_id_fields = ["order", "product"]


@admin.register(CouponCampaign)
class CouponCampaignAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "store",
        "discount_type",
        "discount_value",
        "is_active",
        "starts_at",
        "ends_at",
    ]
    list_filter = ["discount_type", "is_active", "starts_at", "ends_at", "store"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    raw_id_fields = ["store"]


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ["code", "campaign", "customer", "status", "used_at", "created_at"]
    list_filter = ["status", "used_at", "created_at"]
    search_fields = ["code", "customer__email"]
    readonly_fields = ["created_at", "updated_at", "used_at"]
    date_hierarchy = "created_at"
    raw_id_fields = ["campaign", "customer", "order"]


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["name", "store", "method_type", "is_active", "is_default", "created_at"]
    list_filter = ["method_type", "is_active", "is_default", "created_at", "store"]
    search_fields = ["name", "display_name"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    raw_id_fields = ["store"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "payment_method", "amount", "currency", "status", "created_at"]
    list_filter = ["status", "currency", "created_at", "payment_method"]
    search_fields = ["gateway_transaction_id", "customer_email"]
    readonly_fields = ["created_at", "updated_at", "completed_at", "failed_at"]
    date_hierarchy = "created_at"
    raw_id_fields = ["order", "payment_method"]
