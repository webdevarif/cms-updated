import pytest
from django.contrib.auth import get_user_model
from apps.stores.models import Store
from apps.public.forms.models import FormTemplate, FormSubmission

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
def test_formtemplate_store_isolation(store_a, store_b):
    """Test FormTemplate is isolated by store"""
    form_a = FormTemplate.objects.create(store=store_a, form_id='FORM-A', title='Contact Form')
    form_b = FormTemplate.objects.create(store=store_b, form_id='FORM-B', title='Contact Form')
    
    # Store A should only see its own forms
    assert FormTemplate.objects.filter(store=store_a).count() == 1
    assert FormTemplate.objects.filter(store=store_b).count() == 0

@pytest.mark.django_db
def test_formsubmission_store_isolation(store_a, store_b):
    """Test FormSubmission is isolated by store"""
    form_a = FormTemplate.objects.create(store=store_a, form_id='FORM-A', title='Contact Form')
    form_b = FormTemplate.objects.create(store=store_b, form_id='FORM-B', title='Contact Form')
    
    submission_a = FormSubmission.objects.create(store=store_a, form_template=form_a, data={'name': 'John'})
    submission_b = FormSubmission.objects.create(store=store_b, form_template=form_b, data={'name': 'Jane'})
    
    # Store A should only see its own submissions
    assert FormSubmission.objects.filter(store=store_a).count() == 1
    assert FormSubmission.objects.filter(store=store_b).count() == 0

@pytest.mark.django_db
def test_cross_store_form_data_leak(store_a, store_b):
    """Test that stores cannot access each other's form data"""
    form_a = FormTemplate.objects.create(store=store_a, form_id='FORM-A', title='Contact Form')
    submission_a = FormSubmission.objects.create(store=store_a, form_template=form_a, data={'name': 'John'})
    
    # Store B should not see Store A's data
    assert FormTemplate.objects.filter(store=store_b).count() == 0
    assert FormSubmission.objects.filter(store=store_b).count() == 0
    
    # Verify data exists for Store A
    assert FormTemplate.objects.filter(store=store_a).count() == 1
    assert FormSubmission.objects.filter(store=store_a).count() == 1
