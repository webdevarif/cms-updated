"""
Customer ecommerce serializers.
"""
from apps.ecommerce.models.cart import Cart, CartItem
from apps.ecommerce.models.collections import ProductCollection
from apps.ecommerce.models.coupons import Coupon, CouponCampaign
from apps.ecommerce.models.customers import CustomerProfile
from apps.ecommerce.models.orders import Order, OrderItem
from apps.ecommerce.models.payments import Payment, PaymentMethod
from apps.ecommerce.models.products import Product, ProductCategory, ProductVariant
from rest_framework import serializers


class ProductCategoryCustomerSerializer(serializers.ModelSerializer):
    """Customer product category serializer"""

    class Meta:
        model = ProductCategory
        fields = ["id", "name", "slug", "description", "image", "parent", "is_active"]


class ProductCustomerSerializer(serializers.ModelSerializer):
    """Customer product serializer"""

    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "price",
            "compare_at_price",
            "sku",
            "category",
            "category_name",
            "is_featured",
            "tags",
            "created_at",
            "updated_at",
        ]


class ProductVariantCustomerSerializer(serializers.ModelSerializer):
    """Customer product variant serializer"""

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "title",
            "price",
            "compare_at_price",
            "sku",
            "quantity",
            "options",
            "effective_price",
        ]


class CartCustomerSerializer(serializers.ModelSerializer):
    """Customer cart serializer"""

    items = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total_amount", "created_at", "updated_at"]

    def get_items(self, obj):
        return CartItemCustomerSerializer(obj.items.all(), many=True).data

    def get_total_amount(self, obj):
        return sum(item.total_price for item in obj.items.all())


class CartItemCustomerSerializer(serializers.ModelSerializer):
    """Customer cart item serializer"""

    product_name = serializers.CharField(source="product.title", read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_name", "quantity", "unit_price", "total_price"]


class CollectionCustomerSerializer(serializers.ModelSerializer):
    """Customer collection serializer"""

    class Meta:
        model = ProductCollection
        fields = ["id", "title", "slug", "description", "is_featured", "created_at", "updated_at"]


class CustomerProfileCustomerSerializer(serializers.ModelSerializer):
    """Customer profile serializer"""

    class Meta:
        model = CustomerProfile
        fields = ["id", "user", "first_name", "last_name", "phone", "created_at", "updated_at"]


class OrderCustomerSerializer(serializers.ModelSerializer):
    """Customer order serializer"""

    items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "status",
            "subtotal",
            "tax_amount",
            "shipping_amount",
            "total_amount",
            "customer_email",
            "customer_phone",
            "notes",
            "items",
            "created_at",
            "updated_at",
        ]

    def get_items(self, obj):
        return OrderItemCustomerSerializer(obj.items.all(), many=True).data


class OrderItemCustomerSerializer(serializers.ModelSerializer):
    """Customer order item serializer"""

    product_name = serializers.CharField(source="product.title", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "quantity",
            "unit_price",
            "total_price",
            "created_at",
        ]


class CouponCustomerSerializer(serializers.ModelSerializer):
    """Customer coupon serializer"""

    class Meta:
        model = Coupon
        fields = ["id", "code", "campaign", "status", "created_at", "used_at"]


class PaymentMethodCustomerSerializer(serializers.ModelSerializer):
    """Customer payment method serializer"""

    class Meta:
        model = PaymentMethod
        fields = [
            "id",
            "name",
            "method_type",
            "display_name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]


class PaymentCustomerSerializer(serializers.ModelSerializer):
    """Customer payment serializer"""

    payment_method_name = serializers.CharField(source="payment_method.name", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "payment_method",
            "payment_method_name",
            "amount",
            "currency",
            "status",
            "created_at",
            "completed_at",
        ]
