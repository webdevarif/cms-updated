"""
API tests for forms module.
"""
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
import factory

User = get_user_model()


# FactoryBoy fixtures
class UserFactory(factory.django.DjangoModelFactory):
    """User factory for test data"""
    class Meta:
        model = User
        django_get_or_create = ('email',)
    
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    password = 'testpass123'


@pytest.mark.django_db
class FormViewSetTests:
    """Form viewset tests for all roles"""
    
    @pytest.fixture
    def admin_user(self):
        """Create admin user fixture"""
        return UserFactory(
            email='admin@example.com',
            is_staff=True,
            is_superuser=True
        )
    
    @pytest.fixture
    def store_owner(self):
        """Create store owner user fixture"""
        user = UserFactory(email='owner@example.com')
        from apps.stores.models import Store
        store = Store.objects.create(
            name='Test Store',
            slug='test-store',
            owner=user
        )
        return store
    
    @pytest.fixture
    def anonymous_client(self):
        """Create anonymous APIClient fixture"""
        return APIClient()
    
    @pytest.fixture
    def authenticated_client(self, admin_user):
        """Create authenticated APIClient fixture"""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        return client
    
    @pytest.fixture
    def form_template(self, store_owner):
        """Create form template fixture"""
        from ..models import FormTemplate
        return FormTemplate.objects.create(
            store=store_owner,
            name='Test Form',
            slug='test-form',
            fields={'name': {'type': 'text', 'required': True}}
        )
    
    # List endpoint tests
    def test_list_forms_as_anonymous(self, anonymous_client):
        """Test listing forms as anonymous"""
        response = anonymous_client.get('/v2/api/forms/')
        assert response.status_code == 200
    
    def test_list_forms_as_admin(self, authenticated_client):
        """Test listing forms as admin"""
        response = authenticated_client.get('/v2/api/forms/')
        assert response.status_code == 200
    
    # Submit endpoint tests
    def test_submit_form_as_anonymous(self, anonymous_client, form_template):
        """Test submitting form as anonymous"""
        response = anonymous_client.post(f'/v2/api/forms/{form_template.form_id}/submit/', {
            'name': 'Test Name'
        })
        assert response.status_code in [200, 201]
    
    # Create endpoint tests
    def test_create_form_as_admin(self, authenticated_client, store_owner):
        """Test creating form as admin"""
        response = authenticated_client.post('/v2/api/forms/', {
            'name': 'New Form',
            'slug': 'new-form',
            'fields': {'name': {'type': 'text', 'required': True}}
        })
        assert response.status_code == 201
    
    def test_create_form_as_anonymous(self, anonymous_client):
        """Test creating form as anonymous (should fail)"""
        response = anonymous_client.post('/v2/api/forms/', {
            'name': 'New Form',
            'slug': 'new-form',
            'fields': {'name': {'type': 'text', 'required': True}}
        })
        assert response.status_code == 401
    
    # Permission tests
    def test_unauthorized_access(self, anonymous_client, form_template):
        """Test unauthorized access"""
        response = anonymous_client.post(f'/v2/api/forms/{form_template.id}/', {
            'name': 'Hacked Form'
        })
        assert response.status_code == 401
        assert 'authentication' in response.data.get('detail', '').lower()
