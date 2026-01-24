import pytest
from django.contrib.auth import get_user_model
from apps.stores.models import Store
from apps.public.task_queue.models import QueueTask

User = get_user_model()

@pytest.fixture
def store_a(db):
    """Create store A"""
    user = User.objects.create_user('user_a', email='a@example.com', password='pass123')
    return Store.objects.create(name='Store A', slug='store-a', owner=user)

@pytest.fixture
def store_b(db):
    """Create store B"""
    user = User.objects.create_user('user_b', email='b@example.com', password='pass123')
    return Store.objects.create(name='Store B', slug='store-b', owner=user)

@pytest.mark.django_db
def test_queuetask_store_isolation(store_a, store_b):
    """Test QueueTask is isolated by store"""
    task_a = QueueTask.objects.create(store=store_a, task_id='TASK-A', task_name='Email Task')
    task_b = QueueTask.objects.create(store=store_b, task_id='TASK-B', task_name='Email Task')
    
    # Store A should only see its own tasks
    assert QueueTask.objects.filter(store=store_a).count() == 1
    assert QueueTask.objects.filter(store=store_b).count() == 0

@pytest.mark.django_db
def test_cross_store_queue_data_leak(store_a, store_b):
    """Test that stores cannot access each other's queue data"""
    task_a = QueueTask.objects.create(store=store_a, task_id='TASK-A', task_name='Email Task')
    
    # Store B should not see Store A's data
    assert QueueTask.objects.filter(store=store_b).count() == 0
    
    # Verify data exists for Store A
    assert QueueTask.objects.filter(store=store_a).count() == 1
