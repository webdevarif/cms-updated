import pytest
from django.contrib.auth import get_user_model
from apps.stores.models import Store
from apps.test.models import TestRun, TestResult

User = get_user_model()

@pytest.fixture
def store_a(db):
    """Create store A"""
    from core.services.store import StoreService
        
    user = UserService.create_user('user_a', email='a@example.com', password='pass123')
    return StoreService.create_store(name='Store A', slug='store-a', owner=user)

@pytest.fixture
def store_b(db):
    """Create store B"""
    from core.services.store import StoreService
        
    user = UserService.create_user('user_b', email='b@example.com', password='pass123')
    return StoreService.create_store(name='Store B', slug='store-b', owner=user)

@pytest.mark.django_db
def test_testrun_store_isolation(store_a, store_b):
    """Test TestRun is isolated by store"""
    run_a = TestRun.objects.create(store=store_a, run_type='api')
    run_b = TestRun.objects.create(store=store_b, run_type='api')
    
    # Store A should only see its own test runs
    assert TestRun.objects.filter(store=store_a).count() == 1
    assert TestRun.objects.filter(store=store_b).count() == 0

@pytest.mark.django_db
def test_testresult_store_isolation(store_a, store_b):
    """Test TestResult is isolated by store"""
    run_a = TestRun.objects.create(store=store_a, run_type='api')
    run_b = TestRun.objects.create(store=store_b, run_type='api')
    
    result_a = TestResult.objects.create(store=store_a, test_run=run_a, app_name='posts', endpoint='/api/posts/', method='GET', role='public')
    result_b = TestResult.objects.create(store=store_b, test_run=run_b, app_name='posts', endpoint='/api/posts/', method='GET', role='public')
    
    # Store A should only see its own test results
    assert TestResult.objects.filter(store=store_a).count() == 1
    assert TestResult.objects.filter(store=store_b).count() == 0

@pytest.mark.django_db
def test_cross_store_test_data_leak(store_a, store_b):
    """Test that stores cannot access each other's test data"""
    run_a = TestRun.objects.create(store=store_a, run_type='api')
    result_a = TestResult.objects.create(store=store_a, test_run=run_a, app_name='posts', endpoint='/api/posts/', method='GET', role='public')
    
    # Store B should not see Store A's data
    assert TestRun.objects.filter(store=store_b).count() == 0
    assert TestResult.objects.filter(store=store_b).count() == 0
    
    # Verify data exists for Store A
    assert TestRun.objects.filter(store=store_a).count() == 1
    assert TestResult.objects.filter(store=store_a).count() == 1
