"""
Dashboard ecommerce serializers.
"""

from apps.ecommerce.models.cart import Cart, CartItem
from apps.ecommerce.models.collections import ProductCollection
from apps.ecommerce.models.coupons import Coupon, CouponCampaign
from apps.ecommerce.models.customers import CustomerProfile
from apps.ecommerce.models.inventory import Inventory
from apps.ecommerce.models.orders import Order, OrderItem
from apps.ecommerce.models.payments import Payment, PaymentMethod
from apps.ecommerce.models.products import Product, ProductCategory, ProductVariant
from rest_framework import serializers


class ProductCategoryDashboardSerializer(serializers.ModelSerializer):
    """Dashboard product category serializer"""

    product_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image",
            "parent",
            "is_active",
            "product_count",
            "created_at",
            "updated_at",
        ]

    def get_product_count(self, obj):
        return obj.products.filter(status="active").count()


class DashboardProductSerializer(serializers.ModelSerializer):
    """Dashboard product serializer"""

    category_name = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    inventory_count = serializers.SerializerMethodField()
    order_count = serializers.SerializerMethodField()
    revenue = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "price",
            "category",
            "category_name",
            "category_slug",
            "status",
            "sku",
            "inventory_count",
            "order_count",
            "revenue",
            "created_at",
            "updated_at",
        ]

    def get_inventory_count(self, obj):
        try:
            return obj.inventory.quantity
        except:
            return 0

    def get_order_count(self, obj):
        return OrderItem.objects.filter(product=obj).count()

    def get_revenue(self, obj):
        from django.db.models import Sum

        total = OrderItem.objects.filter(product=obj, order__status="completed").aggregate(
            total=Sum("price")
        )["total"]
        return round(total, 2) if total else 0


class ProductVariantDashboardSerializer(serializers.ModelSerializer):
    """Dashboard product variant serializer"""

    product_title = serializers.CharField(source="product.title", read_only=True)
    inventory_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "title",
            "sku",
            "price",
            "product",
            "product_title",
            "inventory_count",
        ]

    def get_inventory_count(self, obj):
        try:
            return obj.inventory.quantity
        except:
            return 0


class CartDashboardSerializer(serializers.ModelSerializer):
    """Dashboard cart serializer"""

    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    item_count = serializers.SerializerMethodField()
    total_value = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "store",
            "status",
            "item_count",
            "total_value",
            "created_at",
            "updated_at",
        ]

    def get_item_count(self, obj):
        return obj.items.count()

    def get_total_value(self, obj):
        total = sum(item.quantity * item.unit_price for item in obj.items.all())
        return round(total, 2)


class CartItemDashboardSerializer(serializers.ModelSerializer):
    """Dashboard cart item serializer"""

    product_title = serializers.CharField(source="product.title", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "cart",
            "product",
            "product_title",
            "product_sku",
            "quantity",
            "unit_price",
            "subtotal",
            "created_at",
        ]

    def get_subtotal(self, obj):
        return round(obj.quantity * obj.unit_price, 2)


class DashboardCollectionSerializer(serializers.ModelSerializer):
    """Dashboard collection serializer"""

    product_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductCollection
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "image",
            "product_count",
            "created_at",
            "updated_at",
        ]

    def get_product_count(self, obj):
        return obj.products.filter(status="active").count()


class DashboardInventorySerializer(serializers.ModelSerializer):
    """Dashboard inventory serializer"""

    product_title = serializers.CharField(source="product.title", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    is_low_stock = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = [
            "id",
            "product",
            "product_title",
            "product_sku",
            "quantity",
            "low_stock_threshold",
            "is_low_stock",
            "stock_status",
        ]

    def get_is_low_stock(self, obj):
        return obj.quantity <= obj.low_stock_threshold

    def get_stock_status(self, obj):
        if obj.quantity == 0:
            return "out_of_stock"
        elif obj.quantity <= obj.low_stock_threshold:
            return "low_stock"
        else:
            return "in_stock"


class OrderDashboardSerializer(serializers.ModelSerializer):
    """Dashboard order serializer"""

    customer_email = serializers.EmailField(source="customer.email", read_only=True)
    customer_name = serializers.CharField(source="customer.get_full_name", read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "customer",
            "customer_email",
            "customer_name",
            "store",
            "status",
            "total_amount",
            "item_count",
            "created_at",
            "updated_at",
        ]

    def get_item_count(self, obj):
        return obj.items.count()


class OrderItemDashboardSerializer(serializers.ModelSerializer):
    """Dashboard order item serializer"""

    product_title = serializers.CharField(source="product.title", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "order",
            "product",
            "product_title",
            "product_sku",
            "quantity",
            "unit_price",
            "total_price",
        ]


class CouponCampaignDashboardSerializer(serializers.ModelSerializer):
    """Dashboard coupon campaign serializer"""

    coupon_count = serializers.SerializerMethodField()
    used_count = serializers.SerializerMethodField()

    class Meta:
        model = CouponCampaign
        fields = [
            "id",
            "name",
            "description",
            "starts_at",
            "ends_at",
            "is_active",
            "coupon_count",
            "used_count",
            "created_at",
        ]

    def get_coupon_count(self, obj):
        return obj.coupons.count()

    def get_used_count(self, obj):
        return obj.coupons.filter(status="used").count()


class CouponDashboardSerializer(serializers.ModelSerializer):
    """Dashboard coupon serializer"""

    campaign_name = serializers.CharField(source="campaign.name", read_only=True)
    customer_email = serializers.EmailField(source="customer.email", read_only=True)

    class Meta:
        model = Coupon
        fields = [
            "id",
            "code",
            "campaign",
            "campaign_name",
            "customer",
            "customer_email",
            "status",
            "used_at",
            "created_at",
        ]


class PaymentMethodDashboardSerializer(serializers.ModelSerializer):
    """Dashboard payment method serializer"""

    usage_count = serializers.SerializerMethodField()

    class Meta:
        model = PaymentMethod
        fields = [
            "id",
            "name",
            "method_type",
            "is_active",
            "usage_count",
            "created_at",
        ]

    def get_usage_count(self, obj):
        return obj.payments.count()


class PaymentDashboardSerializer(serializers.ModelSerializer):
    """Dashboard payment serializer"""

    order_number = serializers.CharField(source="order.order_number", read_only=True)
    customer_email = serializers.EmailField(source="order.customer.email", read_only=True)
    method_name = serializers.CharField(source="payment_method.name", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "order_number",
            "customer_email",
            "payment_method",
            "method_name",
            "amount",
            "currency",
            "status",
            "gateway_transaction_id",
            "created_at",
        ]


class CustomerProfileDashboardSerializer(serializers.ModelSerializer):
    """Dashboard customer profile serializer"""

    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    order_count = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()

    class Meta:
        model = CustomerProfile
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "phone",
            "order_count",
            "total_spent",
            "created_at",
            "updated_at",
        ]

    def get_order_count(self, obj):
        return Order.objects.filter(customer=obj.user).count()

    def get_total_spent(self, obj):
        from django.db.models import Sum

        total = Order.objects.filter(customer=obj.user, status="completed").aggregate(
            total=Sum("total_amount")
        )["total"]
        return round(total, 2) if total else 0
