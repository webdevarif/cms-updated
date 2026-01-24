"""
Customer, Collection, and Coupon models.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Customer(models.Model):
    """Customer profile linked to global user with GDPR compliance"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    
    # Customer info
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('', 'Not Specified')
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    
    # Marketing preferences
    email_marketing = models.BooleanField(default=True)
    sms_marketing = models.BooleanField(default=False)
    
    # Statistics
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_count = models.IntegerField(default=0)
    last_order_at = models.DateTimeField(null=True, blank=True)
    
    # Addresses
    default_billing_address = models.JSONField(default=dict)
    default_shipping_address = models.JSONField(default=dict)
    
    # Metadata
    tags = models.JSONField(default=list)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['store', 'email']]
        indexes = [
            models.Index(fields=['store', 'email']),
            models.Index(fields=['store', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def get_full_name(self):
        """Get customer's full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_personal_data(self):
        """
        Get all personal data for GDPR export
        As per 06-security.md: GDPR compliance requirements
        """
        from ..models import Order, OrderItem
        
        return {
            'user': {
                'email': self.user.email,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'date_joined': self.user.date_joined.isoformat(),
                'last_login': self.user.last_login.isoformat() if self.user.last_login else None
            },
            'customer': {
                'first_name': self.first_name,
                'last_name': self.last_name,
                'email': self.email,
                'phone': self.phone,
                'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
                'gender': self.gender,
                'addresses': {
                    'billing': self.default_billing_address,
                    'shipping': self.default_shipping_address
                },
                'marketing_preferences': {
                    'email_marketing': self.email_marketing,
                    'sms_marketing': self.sms_marketing
                },
                'statistics': {
                    'total_spent': str(self.total_spent),
                    'order_count': self.order_count,
                    'last_order_at': self.last_order_at.isoformat() if self.last_order_at else None
                },
                'tags': self.tags,
                'notes': self.notes,
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat()
            },
            'orders': [
                {
                    'order_number': order.order_number,
                    'total': str(order.total),
                    'status': order.status,
                    'created_at': order.created_at.isoformat(),
                    'currency': order.currency,
                    'customer_email': order.customer_email,
                    'customer_phone': order.customer_phone,
                    'items': [
                        {
                            'title': item.title,
                            'sku': item.sku,
                            'quantity': item.quantity,
                            'unit_price': str(item.unit_price),
                            'total': str(item.total)
                        }
                        for item in order.items.all()
                    ]
                }
                for order in Order.objects.filter(customer=self).select_related('items').prefetch_related('items')
            ]
        }
    
    def anonymize_personal_data(self):
        """
        Anonymize personal data for GDPR compliance
        Retains order history but removes personal identifiers
        """
        # Anonymize customer personal data
        self.first_name = 'Anonymous'
        self.last_name = 'Customer'
        self.email = f"anonymous-{self.id}@deleted.local"
        self.phone = ''
        self.date_of_birth = None
        self.gender = ''
        self.default_billing_address = {}
        self.default_shipping_address = {}
        self.notes = 'Personal data anonymized for GDPR compliance'
        
        # Anonymize linked user data
        if self.user:
            self.user.first_name = 'Anonymous'
            self.user.last_name = 'Customer'
            self.user.email = f"anonymous-{self.user.id}@deleted.local"
            self.user.save()
        
        self.save()
        
        # Log anonymization
        from apps.logs.tasks import log_event_async
        log_event_async.delay({
            'event_type': 'CUSTOMER_DATA_ANONYMIZED',
            'message': f"Customer data anonymized for GDPR compliance: {self.id}",
            'store': self.store,
            'entity_type': 'Customer',
            'entity_id': self.id,
            'metadata': {
                'anonymized_at': timezone.now().isoformat()
            }
        })
    
    def delete_personal_data(self):
        """
        Delete all personal data for GDPR compliance
        Complete removal including order history
        """
        # Delete customer profile
        customer_id = self.id
        store_id = self.store.id
        
        # Delete related orders
        from ..models import Order
        Order.objects.filter(customer=self).delete()
        
        # Delete customer
        self.delete()
        
        # Log deletion
        from apps.logs.tasks import log_event_async
        log_event_async.delay({
            'event_type': 'CUSTOMER_DATA_DELETED',
            'message': f"Customer data deleted for GDPR compliance: {customer_id}",
            'store': store_id,
            'entity_type': 'Customer',
            'entity_id': customer_id,
            'metadata': {
                'deleted_at': timezone.now().isoformat()
            }
        })
    
    class Meta:
        app_label = 'ecommerce'
        db_table = 'ecommerce_customer'
        unique_together = [['user', 'store']]
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['total_spent']),
            models.Index(fields=['order_count']),
            models.Index(fields=['last_order_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.store.name}"
    
    def get_full_name(self):
        """Get customer full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def update_statistics(self):
        """Update customer order statistics"""
        from ..cart import Order
        from django.db.models import Sum
        
        orders = Order.objects.filter(customer=self)
        self.order_count = orders.count()
        self.total_spent = orders.aggregate(total=Sum('total'))['total'] or 0
        last_order = orders.order_by('-created_at').first()
        if last_order:
            self.last_order_at = last_order.created_at
        self.save()


class Collection(models.Model):
    """Product collection/category"""
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    
    # Display
    image = models.ForeignKey(
        'mediafile.MediaFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='collection_images'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'ecommerce'
        db_table = 'ecommerce_collection'
        unique_together = [['store', 'slug']]
    
    def __str__(self):
        return self.name


class Coupon(models.Model):
    """Discount coupon"""
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    code = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    # Discount
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('free_shipping', 'Free Shipping')
    ]
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Validity
    starts_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'ecommerce'
        db_table = 'ecommerce_coupon'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.discount_value}"
