# Ecommerce Security

## 6. Security and Privacy Rules

### 6.1 Data Protection

#### GDPR Compliance
```python
# Customer data handling
class Customer(models.Model):
    # ... fields
    
    def get_personal_data(self):
        """Get all personal data for GDPR export"""
        return {
            'user': {
                'email': self.user.email,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'date_joined': self.user.date_joined.isoformat()
            },
            'customer': {
                'first_name': self.first_name,
                'last_name': self.last_name,
                'email': self.email,
                'phone': self.phone,
                'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
                'addresses': {
                    'billing': self.default_billing_address,
                    'shipping': self.default_shipping_address
                }
            },
            'orders': [
                {
                    'order_number': order.order_number,
                    'total': str(order.total),
                    'created_at': order.created_at.isoformat(),
                    'items': [
                        {
                            'title': item.title,
                            'quantity': item.quantity,
                            'price': str(item.unit_price)
                        }
                        for item in order.items.all()
                    ]
                }
                for order in Order.objects.filter(customer=self)
            ]
        }
    
    def anonymize_data(self):
        """Anonymize customer data for GDPR right to be forgotten"""
        # Anonymize user data
        self.user.email = f"deleted_{self.user.id}@deleted.com"
        self.user.first_name = "Deleted"
        self.user.last_name = "User"
        self.user.save()
        
        # Anonymize customer data
        self.email = f"deleted_{self.id}@deleted.com"
        self.first_name = "Deleted"
        self.last_name = "User"
        self.phone = ""
        self.default_billing_address = {}
        self.default_shipping_address = {}
        self.save()
        
        # Log anonymization
        log_event_async(
            user=None,
            store=None,
            action='customer_data_anonymized',
            object_type='customer',
            object_id=self.id,
            details={'reason': 'GDPR request'}
        )
```

#### Data Encryption
```python
# Sensitive data encryption
from django_cryptography.fields import encrypt

class Payment(models.Model):
    # ... fields
    
    # Encrypt sensitive payment data
    gateway_response = encrypt(models.JSONField(default=dict))
    billing_address = encrypt(models.JSONField(default=dict))
    
    class Meta:
        # Ensure encrypted fields are not logged
        exclude_logs = ['gateway_response', 'billing_address']

class Order(models.Model):
    # ... fields
    
    # Encrypt customer addresses
    billing_address = encrypt(models.JSONField(default=dict))
    shipping_address = encrypt(models.JSONField(default=dict))
    customer_notes = encrypt(models.TextField(blank=True))
```

### 6.2 Access Control

#### Store Isolation
```python
# Strict store-scoped permissions
class StoreScopedPermission(permissions.BasePermission):
    """Ensure users can only access their own store data"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Superuser can access all stores
        if request.user.is_superuser:
            return True
        
        # Get store from request
        store = getattr(request, 'store', None)
        if not store:
            return False
        
        # Check user has access to store
        return request.user.stores.filter(id=store.id).exists()
    
    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, 'store'):
            return True
        
        if request.user.is_superuser:
            return True
        
        return obj.store == request.store

# Apply to all ecommerce ViewSets
class ProductViewSet(StoreScopedViewSet):
    permission_classes = [IsAuthenticated, StoreScopedPermission]
    # ... rest of ViewSet
```

#### Role-based Permissions
```python
# Store membership roles
class StoreMembership(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('viewer', 'Viewer')
    ]
    
    user = models.ForeignKey(GlobalUser, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    class Meta:
        unique_together = ['user', 'store']

# Role-based permissions
class EcommerceRolePermission:
    """Define permissions for each role"""
    
    PERMISSIONS = {
        'owner': ['*'],  # All permissions
        'admin': [
            'product.create', 'product.read', 'product.update', 'product.delete',
            'order.create', 'order.read', 'order.update',
            'customer.create', 'customer.read', 'customer.update',
            'coupon.create', 'coupon.read', 'coupon.update', 'coupon.delete',
            'collection.create', 'collection.read', 'collection.update', 'collection.delete'
        ],
        'manager': [
            'product.create', 'product.read', 'product.update',
            'order.read', 'order.update',
            'customer.read', 'customer.update',
            'coupon.read', 'coupon.create', 'coupon.update',
            'collection.read', 'collection.create', 'collection.update'
        ],
        'staff': [
            'product.read', 'product.update',
            'order.read', 'order.update',
            'customer.read',
            'coupon.read'
        ],
        'viewer': [
            'product.read', 'order.read', 'customer.read', 'coupon.read'
        ]
    }
    
    @classmethod
    def has_permission(cls, user, store, permission):
        """Check if user has specific permission"""
        try:
            membership = StoreMembership.objects.get(user=user, store=store)
            role_permissions = cls.PERMISSIONS.get(membership.role, [])
            
            return '*' in role_permissions or permission in role_permissions
        except StoreMembership.DoesNotExist:
            return False
```

### 6.3 Input Validation

#### Product Data Validation
```python
# Comprehensive validation for product data
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
    
    def validate_title(self, value):
        """Validate product title"""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("Product title must be at least 3 characters")
        
        # Check for malicious content
        if any(keyword in value.lower() for keyword in ['script', 'javascript', 'alert']):
            raise serializers.ValidationError("Invalid characters in title")
        
        return value.strip()
    
    def validate_price(self, value):
        """Validate price values"""
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        
        if value > 999999.99:
            raise serializers.ValidationError("Price exceeds maximum allowed amount")
        
        return value
    
    def validate_sku(self, value):
        """Validate SKU format"""
        if not value:
            raise serializers.ValidationError("SKU is required")
        
        # Check SKU format (alphanumeric with hyphens/underscores)
        import re
        if not re.match(r'^[A-Za-z0-9_-]+$', value):
            raise serializers.ValidationError("SKU can only contain letters, numbers, hyphens, and underscores")
        
        return value.upper()
    
    def validate(self, data):
        """Cross-field validation"""
        # Validate variant prices
        if 'variants' in data:
            for variant in data['variants']:
                if variant.get('price', 0) < 0:
                    raise serializers.ValidationError("Variant price cannot be negative")
                
                if variant.get('compare_at_price') and variant['compare_at_price'] <= variant.get('price', 0):
                    raise serializers.ValidationError("Compare at price must be greater than regular price")
        
        return data
```

#### Order Validation
```python
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
    
    def validate_billing_address(self, value):
        """Validate billing address format"""
        required_fields = ['street', 'city', 'country', 'postal_code']
        
        for field in required_fields:
            if field not in value or not value[field]:
                raise serializers.ValidationError(f"Billing address missing required field: {field}")
        
        # Validate postal code format based on country
        country = value.get('country', '').upper()
        postal_code = value.get('postal_code', '')
        
        if country == 'US' and not re.match(r'^\d{5}(-\d{4})?$', postal_code):
            raise serializers.ValidationError("Invalid US postal code format")
        
        return value
    
    def validate_shipping_address(self, value):
        """Validate shipping address format"""
        return self.validate_billing_address(value)
    
    def validate(self, data):
        """Validate order consistency"""
        # Check if cart belongs to same store
        if 'cart' in data and 'store' in data:
            if data['cart'].store != data['store']:
                raise serializers.ValidationError("Cart must belong to the same store")
        
        # Validate customer belongs to store
        if 'customer' in data and 'store' in data:
            customer_orders = Order.objects.filter(
                customer=data['customer'],
                store=data['store']
            )
            if not customer_orders.exists() and data['customer'].user.stores.filter(id=data['store'].id).exists():
                # First order for this customer in this store
                pass
        
        return data
```

### 6.4 Rate Limiting

#### API Rate Limiting
```python
# Custom rate limiting for ecommerce endpoints
from django.core.cache import cache
from django.http import HttpResponseTooManyRequests
from rest_framework.views import APIView

class EcommerceRateLimitMixin:
    """Rate limiting mixin for ecommerce APIs"""
    
    RATE_LIMITS = {
        'cart': '100/hour',
        'order': '10/hour',
        'payment': '5/hour',
        'product_view': '1000/hour',
        'search': '200/hour'
    }
    
    def get_rate_limit(self, view_name):
        """Get rate limit for specific view"""
        return self.RATE_LIMITS.get(view_name, '100/hour')
    
    def check_rate_limit(self, request, view_name):
        """Check if request exceeds rate limit"""
        if not request.user.is_authenticated:
            # Stricter limits for anonymous users
            limit = self.get_rate_limit(view_name)
            limit = str(int(limit.split('/')[0]) // 2) + '/' + limit.split('/')[1]
        else:
            limit = self.get_rate_limit(view_name)
        
        # Parse limit
        max_requests, period = limit.split('/')
        period_seconds = {'hour': 3600, 'minute': 60, 'second': 1}[period]
        
        # Generate cache key
        if request.user.is_authenticated:
            key = f"rate_limit:{view_name}:{request.user.id}"
        else:
            key = f"rate_limit:{view_name}:{request.META.get('REMOTE_ADDR', 'unknown')}"
        
        # Check current count
        count = cache.get(key, 0)
        
        if count >= int(max_requests):
            return False
        
        # Increment counter
        cache.set(key, count + 1, period_seconds)
        return True
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to check rate limits"""
        view_name = self.__class__.__name__.lower().replace('viewset', '')
        
        if not self.check_rate_limit(request, view_name):
            return HttpResponseTooManyRequests(
                '{"error": "Rate limit exceeded"}',
                content_type='application/json'
            )
        
        return super().dispatch(request, *args, **kwargs)

# Apply to sensitive endpoints
class CartViewSet(EcommerceRateLimitMixin, viewsets.ModelViewSet):
    # ... ViewSet implementation
    pass

class OrderViewSet(EcommerceRateLimitMixin, viewsets.ModelViewSet):
    # ... ViewSet implementation
    pass
```

### 6.5 Payment Security

#### PCI Compliance
```python
# Payment processing security
class PaymentService:
    """Secure payment processing service"""
    
    @staticmethod
    def process_payment(order, payment_method, payment_data):
        """Process payment with security measures"""
        # Validate payment method belongs to store
        if payment_method.store != order.store:
            raise ValidationError("Invalid payment method")
        
        # Never store full credit card details
        sensitive_data = ['card_number', 'cvv', 'expiry']
        
        # Log payment attempt without sensitive data
        log_data = {
            'order_id': order.id,
            'payment_method': payment_method.type,
            'amount': str(order.total),
            'timestamp': timezone.now().isoformat()
        }
        
        try:
            # Process payment through secure gateway
            if payment_method.type == 'stripe':
                result = PaymentService._process_stripe_payment(
                    payment_method, payment_data, order
                )
            elif payment_method.type == 'paypal':
                result = PaymentService._process_paypal_payment(
                    payment_method, payment_data, order
                )
            else:
                raise ValidationError("Unsupported payment method")
            
            # Log successful payment (without sensitive data)
            log_data['status'] = 'success'
            log_data['transaction_id'] = result.get('transaction_id', '')
            log_event_async(
                user=None,
                store=order.store,
                action='payment_processed',
                object_type='payment',
                details=log_data
            )
            
            return result
            
        except Exception as e:
            # Log failed payment
            log_data['status'] = 'failed'
            log_data['error'] = str(e)
            log_event_async(
                user=None,
                store=order.store,
                action='payment_failed',
                object_type='payment',
                details=log_data
            )
            
            raise
    
    @staticmethod
    def _process_stripe_payment(payment_method, payment_data, order):
        """Process Stripe payment securely"""
        import stripe
        
        stripe.api_key = payment_method.config.get('secret_key')
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(order.total * 100),  # Convert to cents
            currency=order.currency.lower(),
            payment_method=payment_data.get('payment_method_id'),
            confirmation_method='manual',
            confirm=True
        )
        
        return {
            'status': 'completed' if intent.status == 'succeeded' else 'pending',
            'transaction_id': intent.id,
            'gateway_response': {'status': intent.status}
        }
```

#### Fraud Detection
```python
# Basic fraud detection
class FraudDetectionService:
    """Fraud detection for ecommerce transactions"""
    
    @staticmethod
    def analyze_order(order):
        """Analyze order for fraud indicators"""
        risk_score = 0
        indicators = []
        
        # Check order value
        if order.total > 1000:
            risk_score += 20
            indicators.append('high_value_order')
        
        # Check shipping vs billing address
        if order.billing_address != order.shipping_address:
            risk_score += 10
            indicators.append('address_mismatch')
        
        # Check customer order history
        if order.customer.order_count == 0:
            risk_score += 15
            indicators.append('first_time_customer')
        
        # Check order frequency
        recent_orders = Order.objects.filter(
            customer=order.customer,
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        if recent_orders > 5:
            risk_score += 25
            indicators.append('high_frequency_orders')
        
        # Check IP address (if available)
        # This would require storing IP addresses with orders
        
        return {
            'risk_score': risk_score,
            'indicators': indicators,
            'is_suspicious': risk_score > 50
        }
    
    @staticmethod
    def flag_suspicious_order(order):
        """Flag suspicious order for review"""
        analysis = FraudDetectionService.analyze_order(order)
        
        if analysis['is_suspicious']:
            order.status = 'flagged'
            order.save()
            
            # Notify admin
            send_fraud_alert_email.delay(order.id, analysis)
            
            # Log fraud detection
            log_event_async(
                user=None,
                store=order.store,
                action='order_flagged_fraud',
                object_type='order',
                object_id=order.id,
                details=analysis
            )
        
        return analysis
```

### 6.6 Data Privacy

#### Customer Consent Management
```python
# Marketing consent tracking
class CustomerConsent(models.Model):
    """Track customer consent for marketing and data processing"""
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    consent_type = models.CharField(max_length=50)  # 'email_marketing', 'sms_marketing', 'data_processing'
    granted = models.BooleanField(default=False)
    granted_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['customer', 'consent_type']

class ConsentService:
    """Manage customer consent"""
    
    @staticmethod
    def record_consent(customer, consent_type, granted, request=None):
        """Record customer consent"""
        consent, created = CustomerConsent.objects.get_or_create(
            customer=customer,
            consent_type=consent_type,
            defaults={
                'granted': granted,
                'granted_at': timezone.now() if granted else None,
                'revoked_at': timezone.now() if not granted else None
            }
        )
        
        if not created:
            consent.granted = granted
            if granted:
                consent.granted_at = timezone.now()
                consent.revoked_at = None
            else:
                consent.revoked_at = timezone.now()
            consent.save()
        
        # Record request details if available
        if request:
            consent.ip_address = request.META.get('REMOTE_ADDR')
            consent.user_agent = request.META.get('HTTP_USER_AGENT', '')
            consent.save()
        
        # Log consent change
        log_event_async(
            user=customer.user,
            store=None,
            action=f'consent_{consent_type}',
            object_type='customer_consent',
            object_id=consent.id,
            details={
                'granted': granted,
                'ip_address': consent.ip_address
            }
        )
        
        return consent
    
    @staticmethod
    def has_consent(customer, consent_type):
        """Check if customer has granted consent"""
        try:
            consent = CustomerConsent.objects.get(
                customer=customer,
                consent_type=consent_type
            )
            return consent.granted and consent.revoked_at is None
        except CustomerConsent.DoesNotExist:
            return False
```

### 6.7 Security Headers

#### API Security Headers
```python
# Security middleware for ecommerce APIs
class EcommerceSecurityMiddleware:
    """Add security headers to ecommerce responses"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://js.stripe.com; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.stripe.com;"
        )
        
        # Remove server information
        response.pop('Server', None)
        
        return response
```

### 6.8 Audit Logging

#### Comprehensive Audit Trail
```python
# Enhanced audit logging for ecommerce
class EcommerceAuditLog(models.Model):
    """Detailed audit log for ecommerce operations"""
    
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    user = models.ForeignKey(GlobalUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=50)
    object_id = models.CharField(max_length=50)
    old_values = models.JSONField(default=dict)
    new_values = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['store', 'action']),
            models.Index(fields=['object_type', 'object_id']),
            models.Index(fields=['timestamp']),
        ]

# Signal handlers for audit logging
@receiver(post_save, sender=Product)
def audit_product_change(sender, instance, created, **kwargs):
    """Audit product changes"""
    if created:
        EcommerceAuditLog.objects.create(
            store=instance.store,
            user=instance.created_by,
            action='product_created',
            object_type='product',
            object_id=instance.id,
            new_values={
                'title': instance.title,
                'sku': instance.sku,
                'status': instance.status,
                'price': str(instance.variants.first().price) if instance.variants.exists() else '0'
            }
        )
    else:
        # Track field changes
        old_instance = sender.objects.get(id=instance.id)
        changes = {}
        
        for field in ['title', 'status', 'featured']:
            old_value = getattr(old_instance, field)
            new_value = getattr(instance, field)
            if old_value != new_value:
                changes[field] = {'old': old_value, 'new': new_value}
        
        if changes:
            EcommerceAuditLog.objects.create(
                store=instance.store,
                user=getattr(instance, 'updated_by', None),
                action='product_updated',
                object_type='product',
                object_id=instance.id,
                old_values=changes
            )
```

### 6.9 Security Best Practices

#### Input Sanitization
```python
# Sanitize all user inputs
import bleach
from django.utils.html import strip_tags

class SanitizedCharField(models.CharField):
    """CharField that automatically sanitizes input"""
    
    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if value:
            # Remove HTML tags and sanitize
            clean_value = bleach.clean(value, tags=[], strip=True)
            setattr(model_instance, self.attname, clean_value)
        return value

class SanitizedTextField(models.TextField):
    """TextField that automatically sanitizes input"""
    
    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if value:
            # Allow limited HTML tags for descriptions
            allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li']
            clean_value = bleach.clean(value, tags=allowed_tags, strip=True)
            setattr(model_instance, self.attname, clean_value)
        return value

# Usage in models
class Product(models.Model):
    title = SanitizedCharField(max_length=255)
    description = SanitizedTextField(blank=True)
    # ... other fields
```

#### SQL Injection Prevention
```python
# Use Django ORM properly to prevent SQL injection
class ProductQuerySet(models.QuerySet):
    """Safe custom queries for products"""
    
    def by_price_range(self, min_price, max_price):
        """Safe price range filtering"""
        return self.filter(
            variants__price__gte=min_price,
            variants__price__lte=max_price
        )
    
    def search_safely(self, query):
        """Safe search implementation"""
        return self.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(sku__icontains=query)
        )

# Never use raw SQL with user input
# BAD: Product.objects.raw(f"SELECT * FROM product WHERE title LIKE '%{user_input}%'")
# GOOD: Product.objects.filter(title__icontains=user_input)
```
