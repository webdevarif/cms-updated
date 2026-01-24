"""
Serializers for customer ecommerce API v2.
"""
from rest_framework import serializers
from apps.public.ecommerce.v2.serializers import (
    ProductSerializer as PublicProductSerializer,
    ProductVariantSerializer as PublicProductVariantSerializer,
    CartItemSerializer as PublicCartItemSerializer,
    CartSerializer as PublicCartSerializer,
    OrderItemSerializer as PublicOrderItemSerializer,
    OrderSerializer as PublicOrderSerializer
)
from apps.public.ecommerce.models import Cart, CartItem, Order, OrderItem, Product, ProductVariant


class CustomerProductVariantSerializer(PublicProductVariantSerializer):
    """Serializer for product variants in customer API."""
    class Meta(PublicProductVariantSerializer.Meta):
        fields = [
            'id', 'title', 'sku', 'price_override', 'compare_at_price',
            'inventory_quantity', 'inventory_policy', 'barcode', 'weight',
            'option1', 'option2', 'option3', 'position'
        ]


class CustomerProductSerializer(PublicProductSerializer):
    """Serializer for products in customer API."""
    variants = CustomerProductVariantSerializer(many=True, read_only=True)
    
    class Meta(PublicProductSerializer.Meta):
        fields = [
            'id', 'title', 'description', 'handle', 'product_type', 'vendor',
            'tags', 'price', 'compare_at_price', 'cost', 'sku', 'barcode',
            'inventory_quantity', 'inventory_management', 'inventory_policy',
            'requires_shipping', 'taxable', 'weight', 'weight_unit',
            'variants', 'options', 'images', 'status', 'published_scope',
            'created_at', 'updated_at', 'published_at', 'template_suffix',
            'is_available', 'is_featured', 'is_giftcard', 'giftcard_expiry_days',
            'download_limit', 'download_expiry_days', 'tax_class', 'seo_title',
            'seo_description', 'seo_keywords', 'meta_title', 'meta_description',
            'meta_keywords', 'related_products', 'upsell_products',
            'cross_sell_products', 'view_count', 'wishlist_count',
            'average_rating', 'review_count'
        ]


class CustomerCartItemSerializer(PublicCartItemSerializer):
    """Serializer for cart items in customer API."""
    class Meta(PublicCartItemSerializer.Meta):
        fields = [
            'id', 'cart', 'product', 'variant', 'quantity', 'unit_price',
            'total_price', 'discount_amount', 'tax_amount', 'created_at',
            'updated_at', 'custom_fields'
        ]


class CustomerCartSerializer(PublicCartSerializer):
    """Serializer for carts in customer API."""
    items = CustomerCartItemSerializer(many=True, read_only=True)
    
    class Meta(PublicCartSerializer.Meta):
        fields = [
            'id', 'user', 'session_key', 'status', 'currency', 'subtotal',
            'total', 'total_tax', 'total_discounts', 'total_items',
            'total_weight', 'shipping_address', 'billing_address',
            'shipping_method', 'payment_method', 'discount_codes', 'note',
            'created_at', 'updated_at', 'completed_at', 'abandoned_at',
            'items'
        ]


class CustomerOrderItemSerializer(PublicOrderItemSerializer):
    """Serializer for order items in customer API."""
    class Meta(PublicOrderItemSerializer.Meta):
        fields = [
            'id', 'order', 'product', 'variant', 'title', 'variant_title',
            'sku', 'barcode', 'quantity', 'price', 'compare_at_price',
            'line_price', 'total_discount', 'tax_lines', 'discount_allocations',
            'fulfillment_status', 'requires_shipping', 'gift_card',
            'gift_card_expiry', 'returned_quantity', 'refunded_quantity',
            'return_status', 'created_at', 'updated_at'
        ]


class CustomerOrderSerializer(PublicOrderSerializer):
    """Serializer for orders in customer API."""
    line_items = CustomerOrderItemSerializer(many=True, read_only=True)
    
    class Meta(PublicOrderSerializer.Meta):
        fields = [
            'id', 'order_number', 'name', 'email', 'phone', 'financial_status',
            'fulfillment_status', 'total_price', 'subtotal_price',
            'total_tax', 'total_discounts', 'total_line_items_price',
            'total_shipping_price', 'currency', 'discount_codes', 'note',
            'shipping_address', 'billing_address', 'shipping_lines',
            'tax_lines', 'payment_gateway', 'payment_details', 'customer',
            'customer_locale', 'browser_ip', 'landing_site', 'referring_site',
            'landing_site_ref', 'order_status_url', 'cancelled_at',
            'cancel_reason', 'tags', 'source_name', 'fulfillments',
            'refunds', 'risk_level', 'source_identifier', 'processed_at',
            'created_at', 'updated_at', 'line_items', 'total_weight',
            'shipping_method', 'tracking_company', 'tracking_number',
            'tracking_url', 'tracking_urls', 'shipping_tax', 'taxes_included',
            'order_created_at', 'order_updated_at', 'test', 'confirmed',
            'reference', 'reference_origin', 'metadata', 'private_metadata'
        ]
