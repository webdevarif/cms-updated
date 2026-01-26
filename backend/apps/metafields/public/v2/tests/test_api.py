"""
Endpoint-focused tests for metafields API.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.contenttypes.models import ContentType
from apps.metafields.models.metafield import MetafieldDefinition, Metafield
from apps.stores.models import Store
from django.contrib.auth import get_user_model

User = get_user_model()


class TestMetafieldPublicViewSet(TestCase):
    """Test public metafields API endpoints via HTTP requests"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name="Test Store", 
            domain="test.com",
            owner=self.user
        )
        self.content_type = ContentType.objects.get(model='store')
        
        # Create metafield definition
        self.definition = MetafieldDefinition.objects.create(
            store=self.store,
            name="Test Metafield",
            namespace="test",
            key="test_field",
            type="text",
            is_visible=True,
            is_required=False
        )
        
        # Create metafield
        self.metafield = Metafield.objects.create(
            store=self.store,
            definition=self.definition,
            content_type=self.content_type,
            object_id=self.store.id,
            value_text="Test value"
        )
    
    def test_list_metafields(self):
        """Test listing public metafields"""
        response = self.client.get('/api/v2/metafields/public/metafields/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
    
    def test_retrieve_metafield(self):
        """Test retrieving a specific metafield"""
        response = self.client.get(f'/api/v2/metafields/public/metafields/{self.metafield.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['key'], 'test_field')
    
    def test_for_object_action(self):
        """Test getting metafields for a specific object"""
        response = self.client.get(
            f'/api/v2/metafields/public/metafields/for_object/'
            f'?content_type=store&object_id={self.store.id}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class TestMetafieldCustomerViewSet(TestCase):
    """Test customer metafields API endpoints via HTTP requests"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name="Test Store", 
            domain="test.com",
            owner=self.user
        )
        self.client.force_authenticate(user=self.user)
        self.content_type = ContentType.objects.get(model='store')
        
        # Create metafield definition
        self.definition = MetafieldDefinition.objects.create(
            store=self.store,
            name="Test Metafield",
            namespace="test",
            key="test_field",
            type="text",
            is_visible=True,
            is_required=False
        )
        
        # Create metafield
        self.metafield = Metafield.objects.create(
            store=self.store,
            definition=self.definition,
            content_type=self.content_type,
            object_id=self.store.id,
            value_text="Test value"
        )
    
    def test_list_metafields(self):
        """Test listing customer metafields"""
        response = self.client.get('/api/v2/metafields/customer/metafields/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
    
    def test_create_metafield(self):
        """Test creating a metafield"""
        data = {
            'definition': self.definition.id,
            'content_type': self.content_type.id,
            'object_id': self.store.id,
            'value_text': 'New value'
        }
        response = self.client.post('/api/v2/metafields/customer/metafields/', data)
        self.assertEqual(response.status_code, 201)
    
    def test_bulk_update_metafields(self):
        """Test bulk updating metafields"""
        data = {
            'content_type': 'store',
            'object_id': self.store.id,
            'metafields': {
                'test.test_field': 'Updated value'
            }
        }
        response = self.client.post('/api/v2/metafields/customer/metafields/bulk_update/', data)
        self.assertEqual(response.status_code, 200)


class TestMetafieldDashboardViewSet(TestCase):
    """Test dashboard metafields API endpoints via HTTP requests"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.store = Store.objects.create(
            name="Test Store", 
            domain="test.com",
            owner=self.user
        )
        self.client.force_authenticate(user=self.user)
        self.content_type = ContentType.objects.get(model='store')
        
        # Create metafield definition
        self.definition = MetafieldDefinition.objects.create(
            store=self.store,
            name="Test Metafield",
            namespace="test",
            key="test_field",
            type="text",
            is_visible=True,
            is_required=False
        )
        
        # Create metafield
        self.metafield = Metafield.objects.create(
            store=self.store,
            definition=self.definition,
            content_type=self.content_type,
            object_id=self.store.id,
            value_text="Test value"
        )
    
    def test_list_metafields(self):
        """Test listing dashboard metafields"""
        response = self.client.get('/api/v2/metafields/dashboard/metafields/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
    
    def test_list_metafield_definitions(self):
        """Test listing metafield definitions"""
        response = self.client.get('/api/v2/metafields/dashboard/metafield-definitions/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
    
    def test_create_metafield_definition(self):
        """Test creating a metafield definition"""
        data = {
            'name': 'New Definition',
            'namespace': 'test',
            'key': 'new_field',
            'type': 'text',
            'is_visible': True,
            'is_required': False
        }
        response = self.client.post('/api/v2/metafields/dashboard/metafield-definitions/', data)
        self.assertEqual(response.status_code, 201)
    
    def test_bulk_attach_metafields(self):
        """Test bulk attaching metafields"""
        data = {
            'content_type': 'store',
            'object_ids': [self.store.id],
            'metafield_keys': ['test.test_field']
        }
        response = self.client.post('/api/v2/metafields/dashboard/metafields/bulk_attach/', data)
        self.assertEqual(response.status_code, 200)
