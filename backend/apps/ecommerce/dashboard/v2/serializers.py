"""
Dashboard ecommerce serializers.
"""
from rest_framework import serializers
from apps.ecommerce.models.products import Product, ProductVariant, ProductCategory
from apps.ecommerce.models.cart import Cart, CartItem
from apps.ecommerce.models.collections import ProductCollection
from apps.ecommerce.models.customers import CustomerProfile
from apps.ecommerce.models.inventory import Inventory
from apps.ecommerce.models.orders import Order, OrderItem
from apps.ecommerce.models.coupons import CouponCampaign, Coupon
from apps.ecommerce.models.payments import PaymentMethod, Payment
from apps.ecommerce.models.review import Review


class ProductCategoryDashboardSerializer(serializers.ModelSerializer):
    """Dashboard product category serializer"""
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'slug', 'description', 'image', 'parent',
            'is_active', 'position', 'product_count', 'created_at', 'updated_at'
        ]
    
    def get_product_count(self, obj):
        return obj.products.count()


class DashboardProductSerializer(serializers.ModelSerializer):
    """Dashboard product serializer"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    variant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'description', 'price', 'compare_at_price',
            'sku', 'barcode', 'category', 'category_name', 'status',
            'is_featured', 'tags', 'created_at', 'updated_at', 'variant_count'
        ]
    
    def get_variant_count(self, obj):
        return obj.variants.count()


class ProductVariantDashboardSerializer(serializers.ModelSerializer):
    """Dashboard product variant serializer"""
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'title', 'price', 'compare_at_price', 'sku',
            'barcode', 'quantity', 'position', 'options', 'effective_price'
        ]


class CartDashboardSerializer(serializers.ModelSerializer):
    """Dashboard cart serializer"""
    items_count = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'session_key', 'items_count', 'total_amount',
            'created_at', 'updated_at'
        ]
    
    def get_items_count(self, obj):
        return obj.items.count()
    
    def get_total_amount(self, obj):
        return sum(item.total_price for item in obj.items.all())


class CartItemDashboardSerializer(serializers.ModelSerializer):
    """Dashboard cart item serializer"""
    product_name = serializers.CharField(source='product.title', read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_name', 'quantity', 'unit_price', 'total_price',
            'created_at', 'updated_at'
        ]


class DashboardCollectionSerializer(serializers.ModelSerializer):
    """Dashboard collection serializer"""
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductCollection
        fields = [
            'id', 'name', 'slug', 'description', 'is_active',
            'product_count', 'created_at', 'updated_at'
        ]
    
    def get_product_count(self, obj):
        return obj.products.count()


class DashboardInventorySerializer(serializers.ModelSerializer):
    """Dashboard inventory serializer"""
    product_name = serializers.CharField(source='product.title', read_only=True)
    
    class Meta:
        model = Inventory
        fields = [
            'id', 'product', 'product_name', 'quantity', 'reserved_quantity',
            'created_at', 'updated_at'
        ]


class OrderDashboardSerializer(serializers.ModelSerializer):
    """Dashboard order serializer"""
    items_count = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'customer_name', 'status',
            'subtotal', 'tax_amount', 'shipping_amount', 'total_amount',
            'customer_email', 'customer_phone', 'items_count', 'notes',
            'created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at'
        ]
    
    def get_items_count(self, obj):
        return obj.items.count()
    
    def get_customer_name(self, obj):
        return obj.customer.get_full_name() if obj.customer else obj.customer_email


class OrderItemDashboardSerializer(serializers.ModelSerializer):
    """Dashboard order item serializer"""
    product_name = serializers.CharField(source='product.title', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'quantity',
            'unit_price', 'total_price', 'product_data', 'created_at'
        ]


class CouponCampaignDashboardSerializer(serializers.ModelSerializer):
    """Dashboard coupon campaign serializer"""
    coupon_count = serializers.SerializerMethodField()
    used_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CouponCampaign
        fields = [
            'id', 'name', 'description', 'discount_type', 'discount_value',
            'minimum_amount', 'usage_limit_per_customer', 'total_usage_limit',
            'starts_at', 'ends_at', 'is_active', 'coupon_count', 'used_count',
            'created_at', 'updated_at'
        ]
    
    def get_coupon_count(self, obj):
        return obj.coupons.count()
    
    def get_used_count(self, obj):
        return obj.coupons.filter(status='used').count()


class CouponDashboardSerializer(serializers.ModelSerializer):
    """Dashboard coupon serializer"""
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'campaign', 'campaign_name', 'code', 'customer', 'order',
            'status', 'used_at', 'created_at', 'updated_at'
        ]


class PaymentMethodDashboardSerializer(serializers.ModelSerializer):
    """Dashboard payment method serializer"""
    payment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'name', 'method_type', 'display_name', 'description',
            'is_active', 'is_default', 'processing_fee_percentage',
            'processing_fee_fixed', 'payment_count', 'created_at', 'updated_at'
        ]
    
    def get_payment_count(self, obj):
        return obj.payments.count()


class PaymentDashboardSerializer(serializers.ModelSerializer):
    """Dashboard payment serializer"""
    payment_method_name = serializers.CharField(source='payment_method.name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'order_number', 'payment_method', 'payment_method_name',
            'amount', 'currency', 'status', 'gateway_transaction_id',
            'customer_email', 'refunded_amount', 'created_at', 'updated_at',
            'completed_at', 'failed_at'
        ]


class CustomerProfileDashboardSerializer(serializers.ModelSerializer):
    """Dashboard customer profile serializer"""
    order_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerProfile
        fields = [
            'id', 'user', 'phone', 'address', 'city', 'country',
            'order_count', 'created_at', 'updated_at'
        ]
    
    def get_order_count(self, obj):
        return Order.objects.filter(customer=obj.user).count()


class ReviewDashboardSerializer(serializers.ModelSerializer):
    """Dashboard review serializer for moderation and analytics"""
    user_display_name = serializers.CharField(source='user.get_display_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    product_title = serializers.CharField(source='product.title', read_only=True)
    replies = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'rating', 'title', 'content', 'user_display_name', 'user_email', 'product_title',
            'created_at', 'updated_at', 'is_approved', 'is_featured', 'verified_purchase',
            'helpful_votes', 'total_votes', 'user_ip', 'user_agent', 'referrer', 'replies', 'reply_count'
        ]
        read_only_fields = [
            'id', 'user_display_name', 'user_email', 'product_title',
            'created_at', 'updated_at', 'verified_purchase', 'helpful_votes', 'total_votes',
            'user_ip', 'user_agent', 'referrer', 'replies', 'reply_count'
        ]

    def get_replies(self, obj):
        """Get all replies for this review (including unapproved for moderation)"""
        replies = Review.objects.filter(parent=obj).select_related('user')
        return ReviewDashboardSerializer(replies, many=True, context=self.context).data

    def get_reply_count(self, obj):
        """Get total reply count"""
        return obj.reply_count


class ReviewModerationSerializer(serializers.Serializer):
    """Serializer for review moderation actions"""
    action = serializers.ChoiceField(choices=[
        'approve', 'reject', 'feature', 'unfeature', 'delete'
    ])
    review_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of review IDs to moderate"
    )
    reason = serializers.CharField(
        required=False,
        help_text="Reason for rejection or other action"
    )


class ReviewAnalyticsSerializer(serializers.Serializer):
    """Serializer for review analytics"""
    days = serializers.IntegerField(
        default=30,
        min_value=1,
        max_value=365,
        help_text="Number of days to analyze"
    )
    approved_only = serializers.BooleanField(
        default=False,
        help_text="Include only approved reviews"
    )


class ReplyAsSellerSerializer(serializers.ModelSerializer):
    """Serializer for sellers/admins to reply as seller"""

    class Meta:
        model = Review
        fields = ['content']

    def create(self, validated_data):
        """Create seller reply using ReviewService"""
        from apps.ecommerce.services.review_service import ReviewService
        from apps.ecommerce.models.products import Product

        request = self.context.get('request')
        parent_id = self.context.get('parent_id')
        product_id = self.context.get('product_id')

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
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referrer = request.META.get('HTTP_REFERER', '')

        # Seller replies are auto-approved
        reply = ReviewService.reply_to_review(
            review=parent,
            user=request.user,
            content=validated_data['content']
        )

        return reply

    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
