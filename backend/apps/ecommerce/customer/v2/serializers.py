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
from apps.ecommerce.models.review import Review
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
        fields = ["id", "name", "slug", "description", "is_active", "created_at", "updated_at"]


class CustomerProfileCustomerSerializer(serializers.ModelSerializer):
    """Customer profile serializer"""

    class Meta:
        model = CustomerProfile
        fields = ["id", "user", "phone", "address", "city", "country", "created_at", "updated_at"]


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


class ReviewCustomerSerializer(serializers.ModelSerializer):
    """Customer review serializer for managing own reviews"""

    user_display_name = serializers.CharField(source="user.get_display_name", read_only=True)
    verified_purchase = serializers.BooleanField(read_only=True)
    helpful_percentage = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "rating",
            "title",
            "content",
            "user_display_name",
            "created_at",
            "updated_at",
            "is_approved",
            "verified_purchase",
            "helpful_votes",
            "total_votes",
            "helpful_percentage",
            "can_edit",
            "can_delete",
        ]
        read_only_fields = [
            "id",
            "user_display_name",
            "created_at",
            "updated_at",
            "is_approved",
            "verified_purchase",
            "helpful_votes",
            "total_votes",
            "helpful_percentage",
            "can_edit",
            "can_delete",
        ]

    def get_helpful_percentage(self, obj):
        """Get helpfulness percentage"""
        return obj.helpful_percentage

    def get_can_edit(self, obj):
        """Check if current user can edit this review"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return (
            obj.user == request.user and not obj.is_approved
        )  # Only unapproved reviews can be edited

    def get_can_delete(self, obj):
        """Check if current user can delete this review"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.user == request.user

    def update(self, instance, validated_data):
        """Update review using ReviewService"""
        from apps.ecommerce.services.review_service import ReviewService

        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required")

        return ReviewService.update_review(
            review=instance,
            user=request.user,
            rating=validated_data.get("rating"),
            title=validated_data.get("title"),
            content=validated_data.get("content"),
        )


class ReplyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating replies to reviews (seller/admin only)"""

    class Meta:
        model = Review
        fields = ["content"]

    def create(self, validated_data):
        """Create a reply using ReviewService"""
        from apps.ecommerce.models.products import Product
        from apps.ecommerce.services.review_service import ReviewService

        request = self.context.get("request")
        parent_id = self.context.get("parent_id")
        product_id = self.context.get("product_id")

        if not product_id:
            raise serializers.ValidationError("Product ID is required")

        if not parent_id:
            raise serializers.ValidationError("Parent review ID is required")

        try:
            product = Product.objects.get(id=product_id)
            parent = Review.objects.get(id=parent_id, product=product)
        except (Product.DoesNotExist, Review.DoesNotExist):
            raise serializers.ValidationError("Product or parent review not found")

        # Extract additional data from request
        user_ip = self._get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        referrer = request.META.get("HTTP_REFERER", "")

        reply = ReviewService.reply_to_review(
            review=parent, user=request.user, content=validated_data["content"]
        )

        return reply

    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
