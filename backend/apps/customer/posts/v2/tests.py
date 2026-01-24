"""Customer posts tests."""

from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from apps.posts.v2.models import Post
from apps.posts.v2.models import PostType
from apps.stores.models import Store

User = get_user_model()


class CustomerPostTests(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store', slug='test-store')
        self.user = User.objects.create_user('testuser', email='user@example.com', password='password')
        self.store.users.add(self.user)
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.post_type = PostType.objects.create(name='Blog', slug='blog', store=self.store)

    def test_create_post(self):
        url = reverse('customer-post-list')
        data = {'title': 'Test', 'content': 'Body', 'post_type': self.post_type.id}
        response = self.client.post(url, data, HTTP_X_STORE_ID=self.store.id)
        self.assertEqual(response.status_code, 201)

    def test_list_posts(self):
        Post.objects.create(store=self.store, title='Existing', slug='existing', content='body', post_type=self.post_type)
        url = reverse('customer-post-list')
        response = self.client.get(url, HTTP_X_STORE_ID=self.store.id)
        self.assertEqual(response.status_code, 200)
