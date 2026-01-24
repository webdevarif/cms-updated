"""
Serializers for dashboard ecommerce API v2.
"""
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from apps.public.ecommerce.v2.serializers import (
    ProductSerializer as PublicProductSerializer,
    ProductVariantSerializer as PublicProductVariantSerializer,
    OrderSerializer as PublicOrderSerializer,
    OrderItemSerializer as PublicOrderItemSerializer,
    CartSerializer as PublicCartSerializer,
    CartItemSerializer as PublicCartItemSerializer,
)
from apps.public.ecommerce.models import (
    Product, ProductVariant, Order, OrderItem, Cart, CartItem, 
    Customer, Collection, Coupon, Inventory, InventoryTransaction
)
from apps.public.ecommerce.models.constants import StatusChoices


# ==================== Base Serializers ====================

class BaseDashboardSerializer(serializers.ModelSerializer):
    """Base serializer for dashboard models with common fields."""
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        
        # Add store-based filtering for related fields
        if request and hasattr(request, 'store'):
            store = request.store
            
            # Filter related fields to only show store-specific data
            for field_name, field in fields.items():
                if hasattr(field, 'queryset') and field.queryset is not None:
                    model = field.queryset.model
                    if hasattr(model, 'store'):
                        field.queryset = model.objects.filter(store=store)
        
        return fields


# ==================== Product Serializers ====================

class DashboardProductVariantSerializer(PublicProductVariantSerializer):
    """Serializer for product variants in dashboard API."""
    class Meta(PublicProductVariantSerializer.Meta):
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'sku', 'barcode')


class DashboardProductCreateVariantSerializer(serializers.ModelSerializer):
    """Serializer for creating product variants in dashboard API."""
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'title', 'price', 'compare_at_price', 'cost_price', 'sku', 
            'barcode', 'inventory_quantity', 'inventory_management', 'weight', 
            'weight_unit', 'option1', 'option2', 'option3', 'position'
        ]
        extra_kwargs = {
            'inventory_quantity': {'required': False, 'default': 0},
            'inventory_management': {'required': False, 'default': True},
        }


class DashboardProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating products in dashboard API."""
    variants = DashboardProductCreateVariantSerializer(many=True, required=False)
    collections = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Collection.objects.all(),
        required=False
    )
    
    class Meta:
        model = Product
        fields = [
            'title', 'description', 'handle', 'product_type', 'vendor', 'tags', 
            'published', 'template_suffix', 'status', 'published_scope',
            'variants', 'collections', 'options', 'images', 'image', 'meta_title',
            'meta_description'
        ]
        extra_kwargs = {
            'handle': {'required': False},
            'status': {'default': 'active'},
            'published_scope': {'default': 'global'},
        }


class DashboardProductUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating products in dashboard API."""
    variants = DashboardProductCreateVariantSerializer(many=True, required=False)
    
    class Meta:
        model = Product
        fields = [
            'title', 'description', 'handle', 'product_type', 'vendor', 'tags',
            'published', 'template_suffix', 'status', 'published_scope',
            'variants', 'collections', 'options', 'images', 'image', 'meta_title',
            'meta_description'
        ]
        extra_kwargs = {
            'handle': {'required': False},
        }


class DashboardProductBulkUpdateSerializer(serializers.Serializer):
    """Serializer for bulk updating products."""
    ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )
    data = serializers.DictField()
    
    def validate(self, attrs):
        # Ensure only allowed fields are being updated in bulk
        allowed_fields = {
            'status', 'published', 'vendor', 'product_type', 'tags',
            'meta_title', 'meta_description'
        }
        
        invalid_fields = set(attrs['data'].keys()) - allowed_fields
        if invalid_fields:
            raise serializers.ValidationError({
                'data': f'Bulk update not allowed for fields: {", ".join(invalid_fields)}'
            })
            
        return attrs


class DashboardProductSerializer(PublicProductSerializer):
    """Serializer for products in dashboard API."""
    variants = DashboardProductVariantSerializer(many=True, read_only=True)
    collections = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Collection.objects.all(),
        required=False
    )
    
    class Meta(PublicProductSerializer.Meta):
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'view_count', 'wishlist_count')


# ==================== Order Serializers ====================

class DashboardOrderItemSerializer(PublicOrderItemSerializer):
    """Serializer for order items in dashboard API."""
    class Meta(PublicOrderItemSerializer.Meta):
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class DashboardOrderItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating order items in dashboard API."""
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(),
        source='variant',
        write_only=True
    )
    
    class Meta:
        model = OrderItem
        fields = [
            'variant_id', 'quantity', 'price', 'compare_at_price', 'cost_price',
            'title', 'variant_title', 'sku', 'barcode', 'requires_shipping',
            'taxable', 'gift_card', 'fulfillment_status', 'tax_lines',
            'coupon_allocations', 'duties', 'gift_card_lines', 'properties'
        ]


class DashboardOrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders in dashboard API."""
    line_items = DashboardOrderItemCreateSerializer(many=True, required=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        source='customer',
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Order
        fields = [
            'customer_id', 'email', 'phone', 'note', 'tags', 'line_items',
            'shipping_address', 'billing_address', 'shipping_lines',
            'tax_lines', 'discount_codes', 'payment_terms', 'metafields',
            'shipping_price', 'shipping_tax', 'tax_included', 'currency',
            'test', 'source_name', 'source_identifier', 'referring_site',
            'landing_site', 'browser_ip', 'client_details', 'location_id',
            'fulfillment_status', 'financial_status', 'payment_gateway_names',
            'processing_method', 'checkout_id', 'checkout_token', 'order_number',
            'coupon_applications', 'coupon_allocations', 'total_coupons',
            'total_line_items_price', 'subtotal_price', 'total_price',
            'total_tax', 'total_weight', 'order_status_url', 'cancel_reason',
            'cancelled_at', 'closed_at', 'processed_at', 'checkout_url',
            'confirmed', 'contact_email', 'estimated_taxes', 'presentment_currency',
            'reference', 'source_url', 'taxes_included', 'total_coupons_set',
            'total_price_set', 'total_shipping_price_set', 'total_tax_set',
            'total_tip_received', 'user_id', 'checkout_id', 'app_id',
            'browser_ip', 'landing_site_ref', 'order_number', 'processing_method',
            'source_identifier', 'source_name', 'source_url', 'tags',
            'token', 'user_agent', 'order_status_url', 'shipping_lines',
            'payment_terms', 'metafields'
        ]
        extra_kwargs = {
            'order_number': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }


class DashboardOrderUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating orders in dashboard API."""
    class Meta:
        model = Order
        fields = [
            'email', 'phone', 'note', 'tags', 'shipping_address',
            'billing_address', 'shipping_lines', 'tax_lines',
            'coupon_codes', 'payment_terms', 'metafields', 'shipping_price',
            'shipping_tax', 'tax_included', 'fulfillment_status',
            'financial_status', 'cancel_reason', 'cancelled_at', 'closed_at'
        ]
        extra_kwargs = {
            'email': {'required': False},
            'phone': {'required': False},
        }


class DashboardOrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating order status."""
    status = serializers.ChoiceField(choices=StatusChoices.get_order_choices())
    send_notification = serializers.BooleanField(default=False)
    email_template = serializers.CharField(required=False)
    note = serializers.CharField(required=False, allow_blank=True)


class DashboardOrderSerializer(PublicOrderSerializer):
    """Serializer for orders in dashboard API."""
    line_items = DashboardOrderItemSerializer(many=True, read_only=True)
    customer = serializers.SerializerMethodField()
    
    class Meta(PublicOrderSerializer.Meta):
        fields = '__all__'
        read_only_fields = (
            'created_at', 'updated_at', 'order_number', 'financial_status',
            'subtotal_price', 'total_coupons', 'total_line_items_price',
            'total_price', 'total_tax', 'total_weight', 'order_status_url',
            'processed_at', 'reference', 'source_identifier', 'source_name',
            'source_url', 'token', 'user_agent', 'browser_ip', 'landing_site',
            'landing_site_ref', 'location_id', 'checkout_token', 'checkout_id',
            'app_id', 'client_details', 'payment_gateway_names',
            'processing_method', 'shipping_lines', 'tax_lines', 'discount_codes',
            'payment_terms', 'metafields', 'discount_applications',
            'discount_allocations', 'total_discounts_set', 'total_price_set',
            'total_shipping_price_set', 'total_tax_set', 'total_tip_received',
            'user_id', 'presentment_currency', 'estimated_taxes', 'confirmed',
            'contact_email', 'taxes_included', 'test', 'reference', 'source_url',
            'tags', 'checkout_url', 'processed_at', 'closed_at', 'cancelled_at',
            'cancel_reason', 'fulfillment_status', 'financial_status',
            'shipping_address', 'billing_address', 'shipping_price',
            'shipping_tax', 'tax_included', 'note', 'phone', 'email',
            'order_number', 'created_at', 'updated_at', 'id', 'currency'
        )
    
    def get_customer(self, obj):
        if obj.customer:
            return {
                'id': obj.customer.id,
                'name': obj.customer.name,
                'email': obj.customer.email,
                'phone': obj.customer.phone
            }
        return None


class DashboardCartItemSerializer(PublicCartItemSerializer):
    """Serializer for cart items in dashboard API."""
    class Meta(PublicCartItemSerializer.Meta):
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class DashboardCartItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating cart items in dashboard API."""
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(),
        source='variant',
        write_only=True
    )
    
    class Meta:
        model = CartItem
        fields = [
            'variant_id', 'quantity', 'price', 'compare_at_price', 'cost_price',
            'title', 'variant_title', 'sku', 'barcode', 'requires_shipping',
            'taxable', 'gift_card', 'properties'
        ]


class DashboardCartSerializer(PublicCartSerializer):
    """Serializer for carts in dashboard API."""
    items = DashboardCartItemSerializer(many=True, read_only=True)
    
    class Meta(PublicCartSerializer.Meta):
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'token', 'user_id')
        read_only_fields = ('created_at', 'updated_at', 'completed_at', 'abandoned_at')


# ==================== Customer Serializers ====================

class DashboardCustomerAddressSerializer(serializers.Serializer):
    """Serializer for customer addresses in dashboard API."""
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    company = serializers.CharField(required=False, allow_blank=True)
    address1 = serializers.CharField()
    address2 = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField()
    province = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField()
    zip = serializers.CharField()
    phone = serializers.CharField(required=False, allow_blank=True)
    name = serializers.CharField(required=False)
    province_code = serializers.CharField(required=False, allow_blank=True)
    country_code = serializers.CharField(required=False, allow_blank=True)
    country_name = serializers.CharField(required=False, allow_blank=True)
    default = serializers.BooleanField(required=False, default=False)


class DashboardCustomerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating customers in dashboard API."""
    addresses = DashboardCustomerAddressSerializer(many=True, required=False)
    
    class Meta:
        model = Customer
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'verified_email',
            'tags', 'note', 'tax_exempt', 'accepts_marketing', 'accepts_marketing_updated_at',
            'marketing_opt_in_level', 'currency', 'tax_exemptions', 'admin_graphql_api_id',
            'default_address', 'addresses', 'state', 'total_spent', 'orders_count'
        ]
        extra_kwargs = {
            'verified_email': {'default': True},
            'accepts_marketing': {'default': False},
            'tax_exempt': {'default': False},
            'state': {'read_only': True},
            'total_spent': {'read_only': True},
            'orders_count': {'read_only': True},
        }


class DashboardCustomerUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating customers in dashboard API."""
    class Meta:
        model = Customer
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'verified_email',
            'tags', 'note', 'tax_exempt', 'accepts_marketing', 'state'
        ]
        extra_kwargs = {
            'email': {'required': False},
            'phone': {'required': False},
        }


class DashboardCustomerSerializer(serializers.ModelSerializer):
    """Serializer for customers in dashboard API."""
    addresses = DashboardCustomerAddressSerializer(many=True, required=False)
    
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'total_spent', 'orders_count')


# ==================== Collection Serializers ====================

class DashboardCollectionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating collections in dashboard API."""
    class Meta:
        model = Collection
        fields = [
            'title', 'handle', 'description', 'published', 'image', 'rules',
            'disjunctive', 'sort_order', 'template_suffix', 'seo_title',
            'seo_description', 'metafields', 'published_scope', 'products'
        ]
        extra_kwargs = {
            'handle': {'required': False},
            'published_scope': {'default': 'global'},
        }


class DashboardCollectionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating collections in dashboard API."""
    class Meta:
        model = Collection
        fields = [
            'title', 'handle', 'description', 'published', 'image', 'rules',
            'disjunctive', 'sort_order', 'template_suffix', 'seo_title',
            'seo_description', 'metafields', 'published_scope', 'products'
        ]
        extra_kwargs = {
            'handle': {'required': False},
        }


class DashboardCollectionSerializer(serializers.ModelSerializer):
    """Serializer for collections in dashboard API."""
    products_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Collection
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'handle', 'products_count')


# ==================== Coupon Serializers ====================

class DashboardCouponCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating coupons in dashboard API."""
    class Meta:
        model = Coupon
        fields = [
            'code', 'type', 'value', 'minimum_order_amount', 'usage_limit',
            'usage_limit_per_customer', 'starts_at', 'ends_at', 'status',
            'applies_once_per_customer', 'customer_selection', 'customers'
        ]
        extra_kwargs = {
            'code': {'required': True},
            'type': {'required': True},
            'value': {'required': True},
            'status': {'default': 'active'},
        }


class DashboardCouponUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating coupons in dashboard API."""
    class Meta:
        model = Coupon
        fields = [
            'code', 'type', 'value', 'minimum_order_amount', 'usage_limit',
            'usage_limit_per_customer', 'starts_at', 'ends_at', 'status',
            'applies_once_per_customer', 'customer_selection', 'customers'
        ]
        extra_kwargs = {
            'code': {'required': False},
            'type': {'required': False},
            'value': {'required': False},
        }


class DashboardCouponUsageSerializer(serializers.Serializer):
    """Serializer for coupon usage statistics."""
    total_uses = serializers.IntegerField()
    unique_customers = serializers.IntegerField()
    total_coupon_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    usage_per_day = serializers.ListField(child=serializers.DictField())


class DashboardCouponSerializer(serializers.ModelSerializer):
    """Serializer for coupons in dashboard API."""
    usage = serializers.SerializerMethodField()
    
    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'usage_count')
    
    def get_usage(self, obj):
        # This would be populated in the view with actual usage data
        return self.context.get('usage', None)
        read_only_fields = ('created_at', 'updated_at', 'times_used')


# ==================== Inventory Serializers ====================

class DashboardStockMovementSerializer(serializers.ModelSerializer):
    """Serializer for stock movements in dashboard API."""
    user = serializers.SerializerMethodField()
    inventory_title = serializers.CharField(source='inventory.title', read_only=True)
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'inventory', 'inventory_title', 'transaction_type', 'quantity',
            'counted_quantity', 'note', 'user', 'created_at'
        ]
        read_only_fields = ('created_at', 'user')
    
    def get_user(self, obj):
        if obj.user:
            return {
                'id': obj.user.id,
                'name': obj.user.get_full_name() or obj.user.email,
                'email': obj.user.email
            }
        return None


class DashboardOrderMetricsSerializer(serializers.Serializer):
    """Serializer for order metrics in dashboard API."""
    total_orders = serializers.IntegerField(read_only=True)
    pending_orders = serializers.IntegerField(read_only=True)
    completed_orders = serializers.IntegerField(read_only=True)
    cancelled_orders = serializers.IntegerField(read_only=True)
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    recent_orders = serializers.ListField(read_only=True)


class DashboardRefundCreateSerializer(serializers.Serializer):
    """Serializer for creating order refunds in dashboard API."""
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all()
    )
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reason = serializers.CharField()
    notify_customer = serializers.BooleanField(default=True)
    note = serializers.CharField(required=False, allow_blank=True)


class DashboardFulfillmentCreateSerializer(serializers.Serializer):
    """Serializer for creating order fulfillments in dashboard API."""
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all()
    )
    tracking_number = serializers.CharField(required=False, allow_blank=True)
    tracking_company = serializers.CharField(required=False, allow_blank=True)
    location_id = serializers.CharField(required=False, allow_blank=True)
    notify_customer = serializers.BooleanField(default=True)
    note = serializers.CharField(required=False, allow_blank=True)


class DashboardProductMetricsSerializer(serializers.Serializer):
    """Serializer for product metrics in dashboard API."""
    total_products = serializers.IntegerField(read_only=True)
    active_products = serializers.IntegerField(read_only=True)
    out_of_stock = serializers.IntegerField(read_only=True)
    low_stock = serializers.IntegerField(read_only=True)
    total_value = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    recent_sales = serializers.IntegerField(read_only=True)
    top_products = serializers.ListField(read_only=True)


class DashboardInventoryItemSerializer(serializers.ModelSerializer):
    """Serializer for inventory items in dashboard API."""
    
    class Meta:
        model = Inventory
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class DashboardInventoryAdjustmentSerializer(serializers.Serializer):
    """Serializer for inventory adjustments in dashboard API."""
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all()
    )
    quantity = serializers.IntegerField()
    note = serializers.CharField(required=False, allow_blank=True)
    location_id = serializers.CharField(required=False)
    cost = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        allow_null=True
    )
    reason = serializers.ChoiceField(
        choices=InventoryTransaction.TRANSACTION_TYPES,
        default='manual'
    )


class DashboardInventoryTransferSerializer(serializers.Serializer):
    """Serializer for inventory transfers in dashboard API."""
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all()
    )
    quantity = serializers.IntegerField(min_value=1)
    from_location = serializers.CharField()
    to_location = serializers.CharField()
    note = serializers.CharField(required=False, allow_blank=True)
    expected_arrival = serializers.DateTimeField(required=False, allow_null=True)


class DashboardInventoryCountSerializer(serializers.Serializer):
    """Serializer for inventory counts in dashboard API."""
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all()
    )
    counted_quantity = serializers.IntegerField(min_value=0)
    note = serializers.CharField(required=False, allow_blank=True)
    location_id = serializers.CharField(required=False)
    user_id = serializers.IntegerField(required=False)
    count_date = serializers.DateTimeField(default=timezone.now)
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'inventory', 'transaction_type', 'quantity', 'counted_quantity',
            'note', 'location_id', 'user_id', 'count_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at')


class DashboardStockMovementSerializer(serializers.ModelSerializer):
    """Serializer for stock movements in dashboard API."""
    class Meta:
        model = InventoryTransaction
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'user')
