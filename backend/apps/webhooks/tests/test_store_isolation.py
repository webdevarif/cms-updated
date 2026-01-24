import pytest
from django.contrib.auth import get_user_model
from apps.stores.models import Store
from apps.webhooks.models import WebhookEvent, WebhookDelivery

User = get_user_model()

@pytest.fixture
def store_a(db):
    """Create store A"""
    from core.services.user import UserService
    user = UserService.create_user(email='a@example.com', username='user_a', password='pass123')
    from core.services.store import StoreService
        
    return StoreService.create_store(name='Store A', slug='store-a', owner=user)

@pytest.fixture
def store_b(db):
    """Create store B"""
    from core.services.user import UserService
    user = UserService.create_user(email='b@example.com', username='user_b', password='pass123')
    from core.services.store import StoreService
        
    return StoreService.create_store(name='Store B', slug='store-b', owner=user)

@pytest.mark.django_db
def test_webhookevent_store_isolation(store_a, store_b):
    """Test WebhookEvent is isolated by store"""
    event_a = WebhookEvent.objects.create(store=store_a, event_type='order.created')
    event_b = WebhookEvent.objects.create(store=store_b, event_type='order.created')
    
    # Store A should only see its own events
    assert WebhookEvent.objects.filter(store=store_a).count() == 1
    assert WebhookEvent.objects.filter(store=store_b).count() == 0

@pytest.mark.django_db
def test_webhookdelivery_store_isolation(store_a, store_b):
    """Test WebhookDelivery is isolated by store"""
    from apps.webhooks.models import Webhook
    
    from core.services.webhook import WebhookService
        
    webhook_a = WebhookService.create_webhook(store_a, name='Webhook A', url='https://a.example.com')
    webhook_b = WebhookService.create_webhook(store_b, name='Webhook B', url='https://b.example.com')
    
    delivery_a = WebhookService.create_delivery(webhook_a, store_a, 'order.created')
    delivery_b = WebhookService.create_delivery(webhook_b, store_b, 'order.created')
    
    # Store A should only see its own deliveries
    assert WebhookDelivery.objects.filter(store=store_a).count() == 1
    assert WebhookDelivery.objects.filter(store=store_b).count() == 0

@pytest.mark.django_db
def test_cross_store_webhook_data_leak(store_a, store_b):
    """Test that stores cannot access each other's webhook data"""
    event_a = WebhookEvent.objects.create(store=store_a, event_type='order.created')
    
    # Store B should not see Store A's data
    assert WebhookEvent.objects.filter(store=store_b).count() == 0
    
    # Verify data exists for Store A
    assert WebhookEvent.objects.filter(store=store_a).count() == 1
