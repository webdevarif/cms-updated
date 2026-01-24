"""
Metrics serializers for dashboard ecommerce API v2.
"""
from rest_framework import serializers
from django.utils import timezone
from apps.public.ecommerce.models import Order, OrderItem, ProductVariant, Product


class DashboardOrderMetricsSerializer(serializers.Serializer):
    """Serializer for order metrics."""
    time_series = serializers.ListField(child=serializers.DictField())
    status_distribution = serializers.ListField(child=serializers.DictField())
    sales_by_product = serializers.ListField(child=serializers.DictField())
    sales_by_customer = serializers.ListField(child=serializers.DictField())
    total_orders = serializers.IntegerField()
    total_sales = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    period = serializers.DictField()


class DashboardProductMetricsSerializer(serializers.Serializer):
    """Serializer for product metrics."""
    time_series = serializers.ListField(child=serializers.DictField())
    status_counts = serializers.ListField(child=serializers.DictField())
    top_selling = serializers.ListField(child=serializers.DictField())
    inventory_status = serializers.DictField()
    total_products = serializers.IntegerField()
    total_variants = serializers.IntegerField()
    period = serializers.DictField()


class DashboardInventoryMetricsSerializer(serializers.Serializer):
    """Serializer for inventory metrics."""
    low_stock_items = serializers.ListField(child=serializers.DictField())
    out_of_stock_items = serializers.ListField(child=serializers.DictField())
    inventory_value = serializers.DictField()
    stock_movements = serializers.ListField(child=serializers.DictField())
    period = serializers.DictField()


class DashboardCustomerMetricsSerializer(serializers.Serializer):
    """Serializer for customer metrics."""
    total_customers = serializers.IntegerField()
    new_customers = serializers.IntegerField()
    repeat_customers = serializers.IntegerField()
    average_order_value = serializers.DictField()
    customer_acquisition = serializers.ListField(child=serializers.DictField())
    customer_lifetime_value = serializers.DictField()
    period = serializers.DictField()


class DashboardSalesMetricsSerializer(serializers.Serializer):
    """Serializer for sales metrics."""
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_orders = serializers.IntegerField()
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    conversion_rate = serializers.FloatField()
    refunds = serializers.DecimalField(max_digits=10, decimal_places=2)
    net_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    sales_by_channel = serializers.ListField(child=serializers.DictField())
    sales_by_location = serializers.ListField(child=serializers.DictField())
    period = serializers.DictField()


class DashboardFulfillmentMetricsSerializer(serializers.Serializer):
    """Serializer for fulfillment metrics."""
    total_fulfillments = serializers.IntegerField()
    fulfillment_status = serializers.DictField()
    average_fulfillment_time = serializers.DurationField()
    fulfillment_by_location = serializers.ListField(child=serializers.DictField())
    fulfillment_by_shipping_method = serializers.ListField(child=serializers.DictField())
    period = serializers.DictField()
