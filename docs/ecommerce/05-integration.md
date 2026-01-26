# Ecommerce Integration

## 5. Module Integration

### 5.1 Media Integration

#### Product Images
```python
# Product model with media integration
class Product(models.Model):
    # ... other fields
    featured_image = models.ForeignKey(
        'media.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='featured_products'
    )
    
    def get_all_images(self):
        """Get all product images including variants"""
        image_ids = []
        
        # Product images
        product_images = self.images.all()
        image_ids.extend([img.id for img in product_images])
        
        # Variant images
        for variant in self.variants.all():
            variant_images = variant.images.all()
            image_ids.extend([img.id for img in variant_images])
        
        return MediaFile.objects.filter(id__in=image_ids)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ForeignKey('media.MediaFile', on_delete=models.CASCADE)
    alt_text = models.CharField(max_length=255, blank=True)
    position = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['position']
```

#### Media File Relationships
```python
# In media/models.py - add reverse relationships
class MediaFile(models.Model):
    # ... existing fields
    
    # Ecommerce relationships
    featured_products = GenericRelation(
        Product,
        object_id_field='featured_image_id',
        related_query_name='featured_image_files'
    )
    
    def get_ecommerce_usage(self):
        """Get all ecommerce usage of this media file"""
        usage = {
            'featured_products': self.featured_products.count(),
            'product_images': ProductImage.objects.filter(image=self).count(),
            'variant_images': ProductVariantImage.objects.filter(image=self).count(),
            'category_images': ProductCategory.objects.filter(image=self).count(),
            'collection_images': Collection.objects.filter(image=self).count()
        }
        return usage
```

### 5.2 Accounts Integration

#### Customer Profile
```python
# Customer model linked to GlobalUser
class Customer(models.Model):
    user = models.OneToOneField(GlobalUser, on_delete=models.CASCADE)
    # ... other fields
    
    def get_user_permissions(self):
        """Get user's ecommerce permissions"""
        return self.user.get_all_permissions()
    
    def can_access_store(self, store):
        """Check if customer can access store"""
        return store.is_active and (
            store.is_public or 
            self.user.stores.filter(id=store.id).exists()
        )
```

#### User Registration
```python
# In accounts/services.py
class AccountService:
    @staticmethod
    def register_customer(user_data, store=None):
        """Register new user with customer profile"""
        user = GlobalUser.objects.create_user(
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )
        
        customer = CustomerService.create_customer(user, user_data)
        
        # Add to store if specified
        if store:
            user.stores.add(store)
        
        # Send welcome email
        send_welcome_email.delay(user.id)
        
        return user, customer
```

### 5.3 Stores Integration

#### Store Configuration
```python
# Store model with ecommerce settings
class Store(models.Model):
    # ... existing fields
    
    # Ecommerce settings
    currency = models.CharField(max_length=3, default='USD')
    tax_included = models.BooleanField(default=False)
    allow_guest_checkout = models.BooleanField(default=True)
    require_account_for_purchase = models.BooleanField(default=False)
    
    # Default settings
    default_shipping_method = models.ForeignKey(
        'ecommerce.ShippingMethod',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='default_stores'
    )
    
    default_tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0
    )
    
    def get_ecommerce_settings(self):
        """Get store ecommerce configuration"""
        return {
            'currency': self.currency,
            'tax_included': self.tax_included,
            'allow_guest_checkout': self.allow_guest_checkout,
            'require_account_for_purchase': self.require_account_for_purchase,
            'default_shipping_method': self.default_shipping_method,
            'default_tax_rate': self.default_tax_rate
        }
```

#### Store Scoping
```python
# Base mixin for store-scoped models
class StoreScopedModel(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    
    class Meta:
        abstract = True
    
    def clean(self):
        """Validate store access"""
        if not self.store.is_active:
            raise ValidationError("Store is not active")

# Usage in ecommerce models
class Product(StoreScopedModel):
    # ... fields
    pass

class Order(StoreScopedModel):
    # ... fields
    pass
```

### 5.4 Logs Integration

#### Auto-logging Signals
```python
# In ecommerce/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from logs.services import log_event_async

@receiver(post_save, sender=Product)
def log_product_change(sender, instance, created, **kwargs):
    """Log product changes"""
    action = 'product_created' if created else 'product_updated'
    
    log_event_async(
        user=getattr(instance, 'created_by', None),
        store=instance.store,
        action=action,
        object_type='product',
        object_id=instance.id,
        details={
            'title': instance.title,
            'sku': instance.sku,
            'status': instance.status
        }
    )

@receiver(post_save, sender=Order)
def log_order_change(sender, instance, created, **kwargs):
    """Log order changes"""
    if created:
        log_event_async(
            user=None,  # Orders can be created by customers
            store=instance.store,
            action='order_created',
            object_type='order',
            object_id=instance.id,
            details={
                'order_number': instance.order_number,
                'total': str(instance.total),
                'customer_email': instance.customer.email
            }
        )

@receiver(post_save, sender=Payment)
def log_payment_change(sender, instance, created, **kwargs):
    """Log payment changes"""
    if created:
        log_event_async(
            user=None,
            store=instance.order.store,
            action='payment_created',
            object_type='payment',
            object_id=instance.id,
            details={
                'order_id': instance.order.id,
                'amount': str(instance.amount),
                'status': instance.status
            }
        )
```

#### Manual Logging
```python
# In ecommerce/services.py
class OrderService:
    @staticmethod
    def update_order_status(order, new_status, user=None):
        """Update order status with logging"""
        old_status = order.status
        
        # ... business logic ...
        
        # Log the status change
        log_event_async(
            user=user,
            store=order.store,
            action='order_status_updated',
            object_type='order',
            object_id=order.id,
            details={
                'order_number': order.order_number,
                'old_status': old_status,
                'new_status': new_status
            }
        )
        
        return order
```

### 5.5 Translations Integration

#### Translatable Product Fields
```python
# In ecommerce/models.py
from translations.fields import TranslatableField

class Product(StoreScopedModel):
    # ... other fields
    
    # Translatable fields
    title = TranslatableField()
    description = TranslatableField()
    short_description = TranslatableField()
    seo_title = TranslatableField()
    seo_description = TranslatableField()
    
    def get_translated_title(self, language_code=None):
        """Get translated title"""
        return self.get_translation('title', language_code)
    
    def get_translated_description(self, language_code=None):
        """Get translated description"""
        return self.get_translation('description', language_code)

class ProductCategory(StoreScopedModel):
    # ... other fields
    
    # Translatable fields
    name = TranslatableField()
    description = TranslatableField()
    seo_title = TranslatableField()
    seo_description = TranslatableField()
```

#### Translation Service Integration
```python
# In ecommerce/services.py
from translations.services import TranslationService

class ProductService:
    @staticmethod
    def create_product(store, user, data, language_code=None):
        """Create product with translations"""
        product = Product.objects.create(
            store=store,
            # ... non-translatable fields ...
            created_by=user
        )
        
        # Set translations
        if language_code:
            TranslationService.set_translation(
                object_type='product',
                object_id=product.id,
                field='title',
                language_code=language_code,
                value=data['title']
            )
            
            if 'description' in data:
                TranslationService.set_translation(
                    object_type='product',
                    object_id=product.id,
                    field='description',
                    language_code=language_code,
                    value=data['description']
                )
        
        return product
    
    @staticmethod
    def get_product_with_translations(product, language_code=None):
        """Get product with translated fields"""
        if language_code:
            product.translated_title = product.get_translated_title(language_code)
            product.translated_description = product.get_translated_description(language_code)
        
        return product
```

### 5.6 SMTP Integration

#### Email Notifications
```python
# In ecommerce/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from smtp.services import EmailService

@shared_task
def send_order_confirmation_email(order_id):
    """Send order confirmation email"""
    order = Order.objects.get(id=order_id)
    
    # Get customer's preferred language
    language_code = getattr(order.customer.user, 'language_code', 'en')
    
    # Render email template
    context = {
        'order': order,
        'customer': order.customer,
        'store': order.store,
        'order_items': order.items.all()
    }
    
    html_content = render_to_string(
        f'ecommerce/emails/order_confirmation_{language_code}.html',
        context
    )
    
    text_content = render_to_string(
        f'ecommerce/emails/order_confirmation_{language_code}.txt',
        context
    )
    
    # Send email
    EmailService.send_email(
        store=order.store,
        template_name='order_confirmation',
        recipients=[order.customer.email],
        context=context,
        language_code=language_code
    )

@shared_task
def send_order_status_email(order_id, status):
    """Send order status update email"""
    order = Order.objects.get(id=order_id)
    
    context = {
        'order': order,
        'customer': order.customer,
        'status': status,
        'store': order.store
    }
    
    EmailService.send_email(
        store=order.store,
        template_name='order_status_update',
        recipients=[order.customer.email],
        context=context
    )

@shared_task
def send_low_stock_alert_email(store_id, product_ids):
    """Send low stock alert to store admin"""
    store = Store.objects.get(id=store_id)
    products = Product.objects.filter(id__in=product_ids)
    
    context = {
        'store': store,
        'products': products
    }
    
    # Send to store admin
    admin_emails = store.users.filter(
        storemembership__role__in=['admin', 'manager']
    ).values_list('email', flat=True)
    
    EmailService.send_email(
        store=store,
        template_name='low_stock_alert',
        recipients=list(admin_emails),
        context=context
    )
```

#### Email Templates
```python
# In ecommerce/models.py - email template integration
class EmailTemplate(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    language_code = models.CharField(max_length=10, default='en')
    
    class Meta:
        unique_together = ['store', 'name', 'language_code']

# Predefined ecommerce email templates
ECOMMERCE_EMAIL_TEMPLATES = [
    'order_confirmation',
    'order_status_update',
    'payment_confirmation',
    'shipping_confirmation',
    'delivery_confirmation',
    'refund_confirmation',
    'low_stock_alert',
    'welcome_customer',
    'password_reset',
    'abandoned_cart_reminder'
]
```

### 5.7 Multi-tenant Data Isolation

#### Store-scoped Query Manager
```python
# In ecommerce/managers.py
class StoreScopedManager(models.Manager):
    """Manager for store-scoped queries"""
    
    def for_store(self, store):
        """Filter by store"""
        return self.filter(store=store)
    
    def for_user(self, user):
        """Filter by user's stores"""
        return self.filter(store__in=user.stores.all())

# Usage in models
class Product(StoreScopedModel):
    objects = StoreScopedManager()
    
    class Meta:
        base_manager_name = 'objects'
```

#### Permission Mixins
```python
# In ecommerce/permissions.py
class StoreScopedPermission:
    """Permission mixin for store-scoped access"""
    
    def has_store_permission(self, request, store):
        """Check if user has permission for store"""
        if not store.is_active:
            return False
        
        if request.user.is_superuser:
            return True
        
        return request.user.stores.filter(id=store.id).exists()
    
    def has_object_permission(self, request, view, obj):
        """Check permission for specific object"""
        if hasattr(obj, 'store'):
            return self.has_store_permission(request, obj.store)
        
        return True
```

### 5.8 API Integration

#### Store Context Middleware
```python
# In ecommerce/middleware.py
class StoreContextMiddleware:
    """Middleware to add store context to request"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Determine store from subdomain, header, or user
        store = self.get_store_from_request(request)
        
        if store:
            request.store = store
            request.store_settings = store.get_ecommerce_settings()
        
        response = self.get_response(request)
        return response
    
    def get_store_from_request(self, request):
        """Get store from various sources"""
        # Try subdomain
        host = request.get_host()
        subdomain = host.split('.')[0] if '.' in host else None
        
        if subdomain:
            try:
                return Store.objects.get(subdomain=subdomain, is_active=True)
            except Store.DoesNotExist:
                pass
        
        # Try header
        store_id = request.META.get('HTTP_X_STORE_ID')
        if store_id:
            try:
                return Store.objects.get(id=store_id, is_active=True)
            except Store.DoesNotExist:
                pass
        
        # Try user's default store
        if request.user.is_authenticated:
            return request.user.stores.filter(is_active=True).first()
        
        # Try default store
        return Store.objects.filter(is_default=True, is_active=True).first()
```

#### API Response Formatting
```python
# In ecommerce/serializers.py
class StoreAwareSerializer:
    """Serializer mixin for store-aware responses"""
    
    def to_representation(self, instance):
        """Add store context to response"""
        data = super().to_representation(instance)
        
        if hasattr(instance, 'store'):
            data['store'] = {
                'id': instance.store.id,
                'name': instance.store.name,
                'currency': instance.store.currency
            }
        
        return data

class ProductSerializer(StoreAwareSerializer, serializers.ModelSerializer):
    """Product serializer with store context"""
    
    store_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'description', 'sku', 'status',
            'featured', 'price', 'store_info', 'created_at', 'updated_at'
        ]
    
    def get_store_info(self, obj):
        return {
            'id': obj.store.id,
            'name': obj.store.name,
            'currency': obj.store.currency
        }
```

### 5.9 Event System Integration

#### Ecommerce Events
```python
# In ecommerce/events.py
class EcommerceEvents:
    """Ecommerce event definitions"""
    
    PRODUCT_CREATED = 'product_created'
    PRODUCT_UPDATED = 'product_updated'
    PRODUCT_DELETED = 'product_deleted'
    
    ORDER_CREATED = 'order_created'
    ORDER_UPDATED = 'order_updated'
    ORDER_CANCELLED = 'order_cancelled'
    ORDER_FULFILLED = 'order_fulfilled'
    
    PAYMENT_RECEIVED = 'payment_received'
    PAYMENT_FAILED = 'payment_failed'
    
    CART_ABANDONED = 'cart_abandoned'
    CART_CONVERTED = 'cart_converted'
    
    CUSTOMER_REGISTERED = 'customer_registered'
    CUSTOMER_LOGIN = 'customer_login'
    
    INVENTORY_LOW = 'inventory_low'
    INVENTORY_OUT_OF_STOCK = 'inventory_out_of_stock'

# Event handlers
@receiver(EcommerceEvents.ORDER_CREATED)
def handle_order_created(sender, order, **kwargs):
    """Handle order created event"""
    # Update customer statistics
    order.customer.update_statistics()
    
    # Reserve inventory
    OrderService.reserve_inventory(order)
    
    # Send confirmation email
    send_order_confirmation_email.delay(order.id)
    
    # Log to analytics
    track_analytics_event.delay('order_created', {
        'order_id': order.id,
        'store_id': order.store.id,
        'total': float(order.total),
        'customer_id': order.customer.id
    })
```

### 5.10 Analytics Integration

#### Analytics Tracking
```python
# In ecommerce/analytics.py
class EcommerceAnalytics:
    """Analytics tracking for ecommerce events"""
    
    @staticmethod
    def track_product_view(product, user=None):
        """Track product view"""
        track_event.delay('product_viewed', {
            'product_id': product.id,
            'store_id': product.store.id,
            'user_id': user.id if user else None,
            'timestamp': timezone.now().isoformat()
        })
    
    @staticmethod
    def track_cart_action(cart, action, user=None):
        """Track cart actions"""
        track_event.delay('cart_action', {
            'cart_id': cart.id,
            'store_id': cart.store.id,
            'action': action,  # 'add', 'remove', 'update', 'clear'
            'item_count': cart.get_item_count(),
            'subtotal': float(cart.get_subtotal()),
            'user_id': user.id if user else None,
            'timestamp': timezone.now().isoformat()
        })
    
    @staticmethod
    def track_purchase(order):
        """Track purchase completion"""
        track_event.delay('purchase_completed', {
            'order_id': order.id,
            'store_id': order.store.id,
            'customer_id': order.customer.id,
            'total': float(order.total),
            'item_count': order.items.count(),
            'payment_method': order.payments.first().payment_method.type,
            'timestamp': timezone.now().isoformat()
        })

# Celery task for analytics
@shared_task
def track_analytics_event(event_name, data):
    """Send analytics event to tracking service"""
    # Integration with Google Analytics, Mixpanel, etc.
    pass
```
