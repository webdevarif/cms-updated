"""
Serializers for ecommerce API v2.
"""
from rest_framework import serializers
from ..models import Product, ProductVariant, Cart, CartItem, Order, OrderItem


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for ProductVariant"""
    barcode = serializers.CharField(read_only=True)
    inventory_policy = serializers.CharField(read_only=True)
    weight = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    option1 = serializers.CharField(read_only=True)
    option2 = serializers.CharField(read_only=True)
    option3 = serializers.CharField(read_only=True)
    position = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = ['id', 'title', 'sku', 'barcode', 'price_override', 'compare_at_price', 'cost_price',
                  'inventory_quantity', 'inventory_policy', 'weight', 'option1', 'option2', 'option3', 'position', 'is_available']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product with translation support"""
    variants = ProductVariantSerializer(many=True, read_only=True)
    inventory_status = serializers.CharField(read_only=True)
    product_type = serializers.CharField(read_only=True)
    digital_file = serializers.FileField(read_only=True)
    download_limit = serializers.IntegerField(read_only=True)
    download_expiry_days = serializers.IntegerField(read_only=True)
    is_giftcard = serializers.BooleanField(read_only=True)
    giftcard_expiry_days = serializers.IntegerField(read_only=True)
    tax_class = serializers.CharField(read_only=True)
    featured_image = serializers.ImageField(read_only=True)
    translated_title = serializers.SerializerMethodField()
    translated_description = serializers.SerializerMethodField()
    translated_short_description = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'sku', 'upc', 'description', 'short_description',
            'base_price', 'compare_at_price', 'cost_price',
            'track_inventory', 'inventory_quantity', 'allow_backorder', 'backorder_quantity',
            'requires_shipping', 'weight',
            'status', 'is_featured', 'is_available',
            'seo_title', 'seo_description', 'seo_keywords',
            'primary_image', 'featured_image', 'variants', 'inventory_status',
            'product_type', 'digital_file', 'download_limit', 'download_expiry_days',
            'is_giftcard', 'giftcard_expiry_days', 'tax_class',
            'translated_title', 'translated_description', 'translated_short_description',
            'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'published_at']
    
    def get_translated_field(self, obj, field_name):
        """Get translated field"""
        request = self.context.get('request')
        if not request:
            return getattr(obj, field_name)
        
        language_code = getattr(request, 'LANGUAGE_CODE', 'en')
        store = getattr(request, 'store', None)
        
        # Generate translation key
        key = f"ecommerce.{field_name}.{obj.id}"
        
        from apps.public.translations.services import TranslationService
        return TranslationService.get_translation(key, language_code, store, getattr(obj, field_name))
    
    def get_translated_title(self, obj):
        """Get translated title"""
        return self.get_translated_field(obj, 'title')
    
    def get_translated_description(self, obj):
        """Get translated description"""
        return self.get_translated_field(obj, 'description')
    
    def get_translated_short_description(self, obj):
        """Get translated short description"""
        return self.get_translated_field(obj, 'short_description')


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem"""
    product = ProductSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'variant', 'quantity', 'unit_price', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['id']


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart"""
    items = CartItemSerializer(many=True, read_only=True)
    status = serializers.CharField(read_only=True)
    currency = serializers.CharField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'session_key', 'status', 'currency', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem"""
    product = ProductSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'variant', 'title', 'sku', 'quantity', 'unit_price', 'total_price', 'created_at']
        read_only_fields = ['id']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order"""
    items = OrderItemSerializer(many=True, read_only=True)
    payment_status = serializers.CharField(read_only=True)
    fulfillment_status = serializers.CharField(read_only=True)
    currency = serializers.CharField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'store', 'user', 'order_number', 'status', 'payment_status', 'fulfillment_status',
            'subtotal', 'tax', 'shipping', 'discount', 'total', 'currency',
            'customer_email', 'customer_phone',
            'shipping_name', 'shipping_address1', 'shipping_address2',
            'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country',
            'billing_name', 'billing_address1', 'billing_address2',
            'billing_city', 'billing_state', 'billing_postal_code', 'billing_country',
            'notes', 'customer_notes', 'tags', 'items', 'created_at', 'updated_at', 'shipped_at', 'delivered_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'shipped_at', 'delivered_at']
