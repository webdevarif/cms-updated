# Webhooks App Rules v1.0

## 🎯 Purpose

This document defines strict development rules for the **webhooks** app in CMS-Updated backend, implementing a secure and reliable webhook system for event-driven integrations with external services.

---

## 🏗️ Webhooks App Structure

### **Fixed Directory Structure**
```
apps/
├── webhooks/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── admin.py
│   ├── signals.py
│   ├── services.py
│   ├── tasks.py
│   ├── management/
│   │   └── commands/
│   │       ├── cleanup_webhooks.py
│   │       └── retry_failed_deliveries.py
│   ├── migrations/
│   ├── v2/
│   │   ├── __init__.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_services.py
│       └── test_views.py
```

---

## 📋 Core Models

### **Model Inheritance**
All webhooks models must inherit from `TenantModel` for store scoping:

```python
from core.models import TenantModel
from django.db import models

class Webhook(TenantModel):
    # Store-scoped webhook model
    pass
```

### **Webhook Model**
```python
# apps/webhooks/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import TenantModel
import secrets

User = get_user_model()

class Webhook(TenantModel):
    """
    Store-scoped webhook configuration for external integrations
    """
    
    # Core fields
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Endpoint configuration
    url = models.URLField(max_length=2048)
    method = models.CharField(max_length=10, choices=[('POST', 'POST'), ('PUT', 'PUT')], default='POST')
    
    # Security
    secret = models.CharField(max_length=255, default=secrets.token_urlsafe, help_text="HMAC signature secret")
    verify_ssl = models.BooleanField(default=True, help_text="Verify SSL certificate")
    
    # Event filtering
    events = models.JSONField(default=list, help_text="List of event types to subscribe to")
    event_filter = models.JSONField(default=dict, help_text="Advanced event filtering rules")
    
    # Headers
    headers = models.JSONField(default=dict, help_text="Custom HTTP headers")
    
    # Status
    is_active = models.BooleanField(default=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    
    # Retry configuration
    max_retries = models.PositiveSmallIntegerField(default=5)
    retry_delay = models.PositiveIntegerField(default=60, help_text="Initial retry delay in seconds")
    retry_backoff_multiplier = models.FloatField(default=2.0, help_text="Exponential backoff multiplier")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta(TenantModel.Meta):
        db_table = 'webhooks_webhook'
        unique_together = [['store', 'url']]
        indexes = [
            models.Index(fields=['store', 'is_active']),
            models.Index(fields=['last_triggered_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.url}"
    
    def generate_signature(self, payload):
        """Generate HMAC signature for payload"""
        import hmac
        import hashlib
        import json
        
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self.secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    def is_event_subscribed(self, event_type, event_data=None):
        """Check if webhook should be triggered for this event"""
        # Check if event type is in subscribed events
        if event_type not in self.events:
            return False
        
        # Apply advanced filtering if configured
        if self.event_filter:
            return self._apply_event_filter(event_type, event_data)
        
        return True
    
    def _apply_event_filter(self, event_type, event_data):
        """Apply advanced event filtering rules"""
        # Example filter: {"entity_type": "Order", "status": ["completed", "refunded"]}
        for key, value in self.event_filter.items():
            if key in event_data:
                if isinstance(value, list):
                    if event_data[key] not in value:
                        return False
                elif event_data[key] != value:
                    return False
        return True
```

### **WebhookEvent Model**
```python
class WebhookEvent(TenantModel):
    """
    Represents an event that can trigger webhooks
    """
    
    # Core fields
    event_type = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=[
        ('content', 'Content'),
        ('ecommerce', 'Ecommerce'),
        ('user', 'User'),
        ('system', 'System'),
    ])
    
    # Event schema
    schema = models.JSONField(default=dict, help_text="Event payload schema")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'webhooks_event'
        ordering = ['category', 'event_type']
    
    def __str__(self):
        return f"{self.event_type} ({self.category})"
```

### **WebhookDelivery Model**
```python
class WebhookDelivery(TenantModel):
    """
    Tracks individual webhook delivery attempts
    """
    
    # Relationships
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name='deliveries')
    
    # Event details
    event_type = models.CharField(max_length=100)
    event_id = models.CharField(max_length=100, blank=True)
    
    # Payload
    payload = models.JSONField(default=dict)
    
    # Delivery details
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ], default='pending')
    
    # Response details
    response_status = models.PositiveIntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    response_headers = models.JSONField(default=dict, blank=True)
    
    # Retry tracking
    attempt_number = models.PositiveSmallIntegerField(default=1)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    
    # Timing
    triggered_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    
    # Error details
    error_message = models.TextField(blank=True)
    error_code = models.CharField(max_length=50, blank=True)
    
    class Meta(TenantModel.Meta):
        db_table = 'webhooks_delivery'
        indexes = [
            models.Index(fields=['webhook', 'status']),
            models.Index(fields=['event_type']),
            models.Index(fields=['triggered_at']),
            models.Index(fields=['next_retry_at']),
        ]
        ordering = ['-triggered_at']
    
    def __str__(self):
        return f"Delivery #{self.id} - {self.event_type} ({self.status})"
```

---

## 🔌 API Endpoints

### **V2-Only Implementation**
All webhook endpoints must be V2-only with clean architecture:

#### WebhookViewSet
```python
# apps/webhooks/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsStoreOwner
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class WebhookViewSet(TenantViewSet):
    """
    Webhook management endpoints for dashboard
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    queryset = Webhook.objects.all()
    serializer_class = WebhookSerializer
    filterset_fields = ['is_active']
    search_fields = ['name', 'url', 'description']
    ordering_fields = ['created_at', 'name', 'last_triggered_at']
    ordering = ['-created_at']
    
    @extend_schema(
        summary="Test Webhook",
        description="Send test payload to webhook endpoint",
        responses={200: WebhookDeliverySerializer}
    )
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Send test event to webhook"""
        webhook = self.get_object()
        
        from services.webhook import WebhookService
        delivery = WebhookService.trigger_webhook(
            webhook=webhook,
            event_type='test',
            event_data={'test': True, 'timestamp': timezone.now().isoformat()},
            store=webhook.store
        )
        
        serializer = WebhookDeliverySerializer(delivery)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Regenerate Secret",
        description="Generate new webhook secret",
        responses={200: WebhookSerializer}
    )
    @action(detail=True, methods=['post'])
    def regenerate_secret(self, request, pk=None):
        """Regenerate webhook secret"""
        webhook = self.get_object()
        webhook.secret = secrets.token_urlsafe()
        webhook.save(update_fields=['secret'])
        
        serializer = self.get_serializer(webhook)
        return Response(serializer.data, status=status.HTTP_200_OK)
```

#### WebhookDeliveryViewSet
```python
class WebhookDeliveryViewSet(TenantViewSet):
    """
    Webhook delivery tracking endpoints
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    
    queryset = WebhookDelivery.objects.all()
    serializer_class = WebhookDeliverySerializer
    filterset_fields = ['webhook', 'status', 'event_type']
    ordering_fields = ['triggered_at', 'delivered_at']
    ordering = ['-triggered_at']
```

---

## 🛠️ Services Layer

### **Business Logic Centralization**
All webhook business logic must be in services.py:

#### WebhookService
```python
# apps/webhooks/services.py
import requests
from django.utils import timezone
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class WebhookService:
    """Shared webhook management service"""
    
    @staticmethod
    @transaction.atomic
    def trigger_webhook(webhook, event_type, event_data, store):
        """
        Trigger a webhook with retry logic
        """
        # Check if webhook is subscribed to this event
        if not webhook.is_event_subscribed(event_type, event_data):
            return None
        
        # Create delivery record
        delivery = WebhookDelivery.objects.create(
            webhook=webhook,
            event_type=event_type,
            event_id=event_data.get('id', ''),
            payload=event_data,
            status='pending',
            attempt_number=1
        )
        
        # Update webhook last triggered timestamp
        webhook.last_triggered_at = timezone.now()
        webhook.save(update_fields=['last_triggered_at'])
        
        # Trigger async delivery
        from .tasks import deliver_webhook
        deliver_webhook.delay(delivery.id)
        
        return delivery
    
    @staticmethod
    def deliver_webhook_sync(delivery):
        """
        Synchronous webhook delivery
        """
        webhook = delivery.webhook
        
        # Prepare request
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': webhook.generate_signature(delivery.payload),
            'X-Webhook-Event': delivery.event_type,
            'X-Webhook-ID': str(delivery.id),
            'X-Store-ID': str(webhook.store.id),
            **webhook.headers
        }
        
        # Measure delivery time
        start_time = timezone.now()
        
        try:
            response = requests.request(
                method=webhook.method,
                url=webhook.url,
                json=delivery.payload,
                headers=headers,
                verify=webhook.verify_ssl,
                timeout=30
            )
            
            # Calculate duration
            duration_ms = int((timezone.now() - start_time).total_seconds() * 1000)
            
            # Update delivery
            delivery.response_status = response.status_code
            delivery.response_body = response.text[:10000]  # Limit response body size
            delivery.response_headers = dict(response.headers)
            delivery.delivered_at = timezone.now()
            delivery.duration_ms = duration_ms
            
            # Determine status
            if 200 <= response.status_code < 300:
                delivery.status = 'success'
            else:
                delivery.status = 'failed'
                delivery.error_message = f"HTTP {response.status_code}"
                delivery.error_code = 'HTTP_ERROR'
            
            delivery.save(update_fields=[
                'response_status', 'response_body', 'response_headers',
                'delivered_at', 'duration_ms', 'status', 'error_message', 'error_code'
            ])
            
            # Log delivery
            logger.info(
                f"Webhook #{delivery.id} delivered to {webhook.url} "
                f"- Status: {response.status_code} - Duration: {duration_ms}ms"
            )
            
        except requests.exceptions.Timeout:
            delivery.status = 'failed'
            delivery.error_message = 'Request timeout'
            delivery.error_code = 'TIMEOUT'
            delivery.save(update_fields=['status', 'error_message', 'error_code'])
            logger.error(f"Webhook #{delivery.id} timeout")
            
        except requests.exceptions.SSLError as e:
            delivery.status = 'failed'
            delivery.error_message = f'SSL error: {str(e)}'
            delivery.error_code = 'SSL_ERROR'
            delivery.save(update_fields=['status', 'error_message', 'error_code'])
            logger.error(f"Webhook #{delivery.id} SSL error: {e}")
            
        except requests.exceptions.RequestException as e:
            delivery.status = 'failed'
            delivery.error_message = str(e)
            delivery.error_code = 'REQUEST_ERROR'
            delivery.save(update_fields=['status', 'error_message', 'error_code'])
            logger.error(f"Webhook #{delivery.id} request error: {e}")
        
        # Schedule retry if failed and retries remaining
        if delivery.status == 'failed' and delivery.attempt_number < webhook.max_retries:
            WebhookService.schedule_retry(delivery)
        
        return delivery
    
    @staticmethod
    def schedule_retry(delivery):
        """
        Schedule webhook delivery retry with exponential backoff
        """
        webhook = delivery.webhook
        
        # Calculate retry delay with exponential backoff
        retry_delay = webhook.retry_delay * (webhook.retry_backoff_multiplier ** (delivery.attempt_number - 1))
        
        # Update delivery
        delivery.status = 'retrying'
        delivery.attempt_number += 1
        delivery.next_retry_at = timezone.now() + timezone.timedelta(seconds=retry_delay)
        delivery.save(update_fields=['status', 'attempt_number', 'next_retry_at'])
        
        # Schedule retry task
        from .tasks import deliver_webhook
        deliver_webhook.apply_async(
            args=[delivery.id],
            eta=delivery.next_retry_at
        )
        
        logger.info(
            f"Webhook #{delivery.id} scheduled for retry #{delivery.attempt_number} "
            f"in {retry_delay}s"
        )
```

---

## 🔄 Celery Tasks

### **Async Webhook Delivery**
```python
# apps/webhooks/tasks.py
from celery import shared_task
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def deliver_webhook(self, delivery_id):
    """
    Async webhook delivery task
    """
    from .models import WebhookDelivery
    from .services import WebhookService
    
    try:
        delivery = WebhookDelivery.objects.select_related('webhook').get(id=delivery_id)
        
        # Skip if already successful
        if delivery.status == 'success':
            return {'status': 'already_delivered'}
        
        # Deliver webhook
        result = WebhookService.deliver_webhook_sync(delivery)
        
        return {
            'delivery_id': delivery_id,
            'status': result.status,
            'response_status': result.response_status
        }
        
    except WebhookDelivery.DoesNotExist:
        logger.error(f"Webhook delivery #{delivery_id} not found")
        raise
        
    except Exception as exc:
        logger.error(f"Webhook delivery failed: {exc}")
        raise self.retry(exc=exc, countdown=60)

@shared_task
def cleanup_old_deliveries(days=90):
    """
    Clean up old webhook delivery records
    """
    from django.utils import timezone
    from .models import WebhookDelivery
    
    cutoff = timezone.now() - timezone.timedelta(days=days)
    deleted_count = WebhookDelivery.objects.filter(
        triggered_at__lt=cutoff,
        status='success'
    ).delete()[0]
    
    logger.info(f"Cleaned up {deleted_count} old webhook deliveries")
    return deleted_count
```

---

## 🔒 Security Rules

### **Webhook Security**
- **Signature Verification**: All webhooks must use HMAC SHA-256 signatures
- **Secret Management**: Secrets must be cryptographically secure and rotatable
- **SSL Verification**: SSL verification should be enabled by default
- **Rate Limiting**: Implement rate limiting on webhook endpoints
- **Payload Validation**: Validate payload structure before processing
- **URL Validation**: Validate webhook URLs to prevent SSRF attacks
- **Timeout Protection**: Implement request timeouts to prevent hanging
- **Size Limits**: Limit payload and response sizes

### **Signature Verification**
```python
# Example signature verification in external service
import hmac
import hashlib
import json

def verify_webhook_signature(payload, signature, secret):
    """
    Verify webhook signature
    """
    payload_str = json.dumps(payload, sort_keys=True)
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected_signature}", signature)
```

---

## 📊 Performance Rules

### **Delivery Optimization**
- **Async Delivery**: All webhook deliveries must be asynchronous
- **Batch Processing**: Process multiple webhooks in parallel where appropriate
- **Retry Logic**: Implement exponential backoff for retries
- **Queue Management**: Use Celery for delivery queue management
- **Cleanup**: Regular cleanup of old delivery records

### **Database Optimization**
- **Indexes**: Add indexes on frequently queried fields
- **Query Optimization**: Use `select_related` for webhook lookups
- **Bulk Operations**: Use bulk operations for cleanup tasks
- **Partitioning**: Consider partitioning large delivery tables by date

---

## 🧪 Testing Rules

### **Required Coverage**
- **Models**: 95% code coverage
- **Services**: 100% code coverage
- **Views**: 90% code coverage
- **Integration**: Critical path testing

### **Test Examples**
```python
# apps/webhooks/tests/test_services.py
from django.test import TestCase
from django.utils import timezone
from ..models import Webhook, WebhookDelivery
from ..services import WebhookService

class WebhookServiceTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', slug='test-store')
        self.webhook = Webhook.objects.create(
            store=self.store,
            name='Test Webhook',
            url='https://example.com/webhook',
            events=['order.created']
        )
    
    def test_trigger_webhook(self):
        """Test webhook triggering"""
        event_data = {'id': '123', 'status': 'created'}
        delivery = WebhookService.trigger_webhook(
            webhook=self.webhook,
            event_type='order.created',
            event_data=event_data,
            store=self.store
        )
        
        self.assertIsNotNone(delivery)
        self.assertEqual(delivery.event_type, 'order.created')
        self.assertEqual(delivery.status, 'pending')
    
    def test_webhook_not_subscribed(self):
        """Test webhook not subscribed to event"""
        delivery = WebhookService.trigger_webhook(
            webhook=self.webhook,
            event_type='product.created',
            event_data={'id': '456'},
            store=self.store
        )
        
        self.assertIsNone(delivery)
    
    def test_signature_generation(self):
        """Test signature generation"""
        payload = {'test': 'data'}
        signature = self.webhook.generate_signature(payload)
        
        self.assertTrue(signature.startswith('sha256='))
        self.assertEqual(len(signature), 71)  # sha256= + 64 hex chars
```

---

## 🔗 Integration Rules

### **Required Integrations**
- **stores.md**: Store scoping and multi-tenancy
- **logs.md**: Activity logging for webhook events
- **accounts.md**: User authentication and permissions
- **core.md**: TenantModel and TenantViewSet

### **Integration Examples**
```python
# Integration with logs.md for event logging
from services.log import LogService

def log_webhook_event(delivery):
    """Log webhook delivery event"""
    LogService.log_event(
        event_type='webhook_delivered',
        level='INFO',
        message=f"Webhook #{delivery.id} delivered to {delivery.webhook.url}",
        store=delivery.webhook.store,
        metadata={
            'webhook_id': delivery.webhook.id,
            'event_type': delivery.event_type,
            'status': delivery.status,
            'response_status': delivery.response_status
        }
    )

# Integration with ecommerce.md for order events
from signals import order_created

@receiver(order_created)
def trigger_order_webhooks(sender, instance, **kwargs):
    """Trigger webhooks on order creation"""
    webhooks = Webhook.objects.filter(
        store=instance.store,
        is_active=True
    )
    
    event_data = {
        'id': str(instance.id),
        'order_number': instance.order_number,
        'status': instance.status,
        'total': float(instance.total),
        'created_at': instance.created_at.isoformat()
    }
    
    for webhook in webhooks:
        WebhookService.trigger_webhook(
            webhook=webhook,
            event_type='order.created',
            event_data=event_data,
            store=instance.store
        )
```

---

## 📈 Event Types Reference

### **Content Events**
- `page.created` - New page created
- `page.updated` - Page updated
- `page.published` - Page published
- `page.deleted` - Page deleted
- `post.created` - New blog post created
- `post.updated` - Blog post updated
- `post.published` - Blog post published
- `post.deleted` - Blog post deleted

### **Ecommerce Events**
- `product.created` - New product created
- `product.updated` - Product updated
- `product.deleted` - Product deleted
- `order.created` - New order created
- `order.updated` - Order updated
- `order.completed` - Order completed
- `order.refunded` - Order refunded
- `cart.created` - Cart created
- `cart.updated` - Cart updated
- `checkout.completed` - Checkout completed

### **User Events**
- `user.registered` - New user registered
- `user.login` - User logged in
- `user.logout` - User logged out
- `user.updated` - User profile updated

### **System Events**
- `store.created` - New store created
- `store.updated` - Store updated
- `webhook.test` - Test webhook event

---

## 🚀 Deployment Notes

### **Required Dependencies**
```python
# requirements.txt
requests>=2.31.0
celery>=5.3.0
```

### **Celery Configuration**
```python
# settings.py
CELERY_BEAT_SCHEDULE = {
    'cleanup-webhook-deliveries': {
        'task': 'apps.webhooks.tasks.cleanup_old_deliveries',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}
```

### **Monitoring**
- Monitor webhook delivery success rates
- Track retry attempts and failures
- Alert on high failure rates
- Monitor queue sizes

---

## 📚 Best Practices

1. **Always use async delivery** - Never block on webhook delivery
2. **Implement proper retry logic** - Use exponential backoff
3. **Validate all payloads** - Ensure data integrity
4. **Log all deliveries** - Maintain audit trail
5. **Rotate secrets regularly** - Security best practice
6. **Rate limit endpoints** - Prevent abuse
7. **Clean up old records** - Prevent table bloat
8. **Monitor performance** - Track delivery times and success rates
9. **Provide clear error messages** - Help with debugging
10. **Document event schemas** - Ensure external integrators understand payloads

---

## 🔧 Management Commands

### **Cleanup Old Deliveries**
```bash
python manage.py cleanup_webhooks --days=90
```

### **Retry Failed Deliveries**
```bash
python manage.py retry_failed_deliveries --webhook-id=1
```

---

## 📝 API Documentation

### **Base URL**
```
/v2/api/webhooks/
```

### **Endpoints**

#### Webhooks
- `GET /v2/api/webhooks/` - List webhooks
- `POST /v2/api/webhooks/` - Create webhook
- `GET /v2/api/webhooks/{id}/` - Get webhook details
- `PUT /v2/api/webhooks/{id}/` - Update webhook
- `DELETE /v2/api/webhooks/{id}/` - Delete webhook
- `POST /v2/api/webhooks/{id}/test/` - Test webhook
- `POST /v2/api/webhooks/{id}/regenerate_secret/` - Regenerate secret

#### Webhook Deliveries
- `GET /v2/api/webhook-deliveries/` - List deliveries
- `GET /v2/api/webhook-deliveries/{id}/` - Get delivery details

---

## 🎯 Implementation Checklist

- [ ] Create Webhook, WebhookEvent, WebhookDelivery models
- [ ] Implement WebhookService with retry logic
- [ ] Create Celery tasks for async delivery
- [ ] Implement signature verification
- [ ] Create API endpoints (WebhookViewSet, WebhookDeliveryViewSet)
- [ ] Add admin interface
- [ ] Implement event filtering
- [ ] Add rate limiting
- [ ] Create tests (models, services, views)
- [ ] Add monitoring and logging
- [ ] Implement cleanup tasks
- [ ] Create management commands
- [ ] Document event schemas
- [ ] Add integration examples

---

## 📖 Version History

- **v1.0** - Initial version with core webhook functionality
