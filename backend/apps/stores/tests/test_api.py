"""
API tests for stores module.
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


class StoreFactory(factory.django.DjangoModelFactory):
    """Store factory for test data"""
    class Meta:
        model = 'stores.Store'
        django_get_or_create = ('slug',)
    
    name = factory.Sequence(lambda n: f'Store {n}')
    slug = factory.Sequence(lambda n: f'store-{n}')
    owner = factory.SubFactory(UserFactory)
    store_type = 'ecommerce'


class StoreSettingsFactory(factory.django.DjangoModelFactory):
    """Store settings factory for test data"""
    class Meta:
        model = 'stores.StoreSettings'
    
    store = factory.SubFactory(StoreFactory)
    site_name = factory.Faker('company')
    currency = 'USD'
    timezone = 'UTC'


@pytest.mark.django_db
class StoreViewSetTests:
    """Store viewset tests for all roles"""
    
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
        store = StoreFactory(owner=user)
        return store
    
    @pytest.fixture
    def staff_user(self, store_owner):
        """Create staff user fixture"""
        from apps.accounts.models import StoreMember, Role
        
        user = UserFactory(email='staff@example.com')
        
        # Create staff role
        role = Role.objects.create(
            store=store_owner,
            slug='staff',
            name='Staff',
            permissions=['content.read', 'ecommerce.read']
        )
        
        # Assign role to user
        StoreMember.objects.create(
            store=store_owner,
            user=user,
            role=role
        )
        
        return user
    
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
    def store(self, store_owner):
        """Store fixture"""
        return store_owner
    
    # List endpoint tests
    def test_list_stores_as_anonymous(self, anonymous_client):
        """Test listing stores as anonymous user"""
        response = anonymous_client.get('/v2/api/stores/')
        
        assert response.status_code == 200
        assert isinstance(response.data, list)
    
    def test_list_stores_as_admin(self, authenticated_client):
        """Test listing stores as admin"""
        response = authenticated_client.get('/v2/api/stores/')
        
        assert response.status_code == 200
        assert isinstance(response.data, list)
    
    # Retrieve endpoint tests
    def test_retrieve_store_as_anonymous(self, anonymous_client, store):
        """Test retrieving a specific store as anonymous"""
        response = anonymous_client.get(f'/v2/api/stores/{store.id}/')
        
        assert response.status_code == 200
        assert response.data['id'] == store.id
    
    def test_retrieve_nonexistent_store(self, anonymous_client):
        """Test retrieving non-existent store"""
        response = anonymous_client.get('/v2/api/stores/99999/')
        
        assert response.status_code == 404
    
    # Create endpoint tests
    def test_create_store_as_admin(self, authenticated_client):
        """Test creating store as admin"""
        response = authenticated_client.post('/v2/api/stores/', {
            'name': 'New Store',
            'slug': 'new-store',
            'store_type': 'ecommerce'
        })
        
        assert response.status_code == 201
        assert response.data['slug'] == 'new-store'
    
    def test_create_store_as_anonymous(self, anonymous_client):
        """Test creating store as anonymous (should fail)"""
        response = anonymous_client.post('/v2/api/stores/', {
            'name': 'New Store',
            'slug': 'new-store',
            'store_type': 'ecommerce'
        })
        
        assert response.status_code == 401
    
    # Update endpoint tests
    def test_update_store_as_admin(self, authenticated_client, store):
        """Test updating store as admin"""
        response = authenticated_client.put(f'/v2/api/stores/{store.id}/', {
            'name': 'Updated Store',
            'slug': store.slug,
            'store_type': store.store_type
        })
        
        assert response.status_code == 200
        assert response.data['name'] == 'Updated Store'
    
    def test_update_store_as_anonymous(self, anonymous_client, store):
        """Test updating store as anonymous (should fail)"""
        response = anonymous_client.patch(f'/v2/api/stores/{store.id}/', {
            'name': 'Updated Store'
        })
        
        assert response.status_code == 401
    
    def test_partial_update_store_as_staff(self, staff_user, store):
        """Test partial update as staff (should fail)"""
        client = APIClient()
        client.force_authenticate(user=staff_user)
        
        response = client.patch(f'/v2/api/stores/{store.id}/', {
            'name': 'Updated Store'
        })
        
        assert response.status_code == 403
    
    # Delete endpoint tests
    def test_delete_store_as_admin(self, authenticated_client, store):
        """Test deleting store as admin"""
        response = authenticated_client.delete(f'/v2/api/stores/{store.id}/')
        
        assert response.status_code == 204
    
    def test_delete_store_as_staff(self, staff_user, store):
        """Test deleting store as staff (should fail)"""
        client = APIClient()
        client.force_authenticate(user=staff_user)
        
        response = client.delete(f'/v2/api/stores/{store.id}/')
        
        assert response.status_code == 403
    
    # Custom action tests
    def test_analytics_endpoint_as_admin(self, authenticated_client, store):
        """Test analytics endpoint as admin"""
        response = authenticated_client.get(f'/v2/api/stores/{store.id}/analytics/')
        
        assert response.status_code == 200
        assert 'page_views' in response.data
    
    def test_analytics_endpoint_as_anonymous(self, anonymous_client, store):
        """Test analytics endpoint as anonymous (should fail)"""
        response = anonymous_client.get(f'/v2/api/stores/{store.id}/analytics/')
        
        assert response.status_code == 401
    
    # Store filtering tests
    def test_store_filtering_as_owner(self, authenticated_client, store):
        """Test that owner only sees their own stores"""
        # Create another store owned by different user
        other_user = UserFactory(email='other@example.com')
        other_store = StoreFactory(owner=other_user)
        
        # List stores
        response = authenticated_client.get('/v2/api/stores/')
        
        assert response.status_code == 200
        store_ids = [item['id'] for item in response.data]
        assert store.id in store_ids
        assert other_store.id not in store_ids
    
    # Permission tests
    def test_unauthorized_access(self, anonymous_client, store):
        """Test unauthorized access to protected endpoints"""
        response = anonymous_client.patch(f'/v2/api/stores/{store.id}/', {
            'name': 'Hacked Store'
        })
        
        assert response.status_code == 401
        assert 'authentication' in response.data.get('detail', '').lower()
    
    def test_forbidden_access(self, staff_user, store):
        """Test forbidden access to protected endpoints"""
        client = APIClient()
        client.force_authenticate(user=staff_user)
        
        response = client.delete(f'/v2/api/stores/{store.id}/')
        
        assert response.status_code == 403
        assert 'permission' in response.data.get('detail', '').lower()
