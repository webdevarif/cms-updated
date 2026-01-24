"""
Tests for customer entities API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from apps.stores.models import Store
from apps.posts.models import Post
from apps.entities.models import EntityAction

User = get_user_model()


class CustomerEntityViewSetTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', slug='test-store')
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.store.users.add(self.user)
        
        self.post = Post.objects.create(
            store=self.store,
            title='Test Post',
            slug='test-post',
            content='Test content'
        )
        
        # Create like action
        self.like_action = EntityAction.objects.create(
            store=self.store,
            name='Like',
            slug='like',
            action_type='toggle'
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_toggle_like_add(self):
        """Test adding a like"""
        url = reverse('customer-entity-toggle')
        data = {
            'action_slug': 'like',
            'content_type': 'post',
            'object_id': self.post.id
        }
        
        response = self.client.post(url, data, HTTP_X_STORE_ID=self.store.id)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['action'], 'added')
        self.assertIsNotNone(response.data['interaction'])
    
    def test_toggle_like_remove(self):
        """Test removing a like"""
        # Add like first
        url = reverse('customer-entity-toggle')
        data = {
            'action_slug': 'like',
            'content_type': 'post',
            'object_id': self.post.id
        }
        self.client.post(url, data, HTTP_X_STORE_ID=self.store.id)
        
        # Remove like
        response = self.client.post(url, data, HTTP_X_STORE_ID=self.store.id)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['action'], 'removed')
        self.assertIsNone(response.data['interaction'])
    
    def test_stats(self):
        """Test getting entity stats"""
        # Add a like first
        url = reverse('customer-entity-toggle')
        data = {
            'action_slug': 'like',
            'content_type': 'post',
            'object_id': self.post.id
        }
        self.client.post(url, data, HTTP_X_STORE_ID=self.store.id)
        
        # Get stats
        url = reverse('customer-entity-stats')
        response = self.client.get(
            url,
            {'content_type': 'post', 'object_id': self.post.id, 'action_slug': 'like'},
            HTTP_X_STORE_ID=self.store.id
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['user_interactions']), 1)
