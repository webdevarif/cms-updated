"""
Customer pages API tests - endpoint-focused only.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import json

User = get_user_model()


class CustomerPagesAPITests(APITestCase):
    """Test customer pages endpoints"""

    def setUp(self):
        """Set up test data"""
        from apps.stores.models import Store
        from apps.pages.models.pages import Post, PostType

        self.user = User.objects.create_user(
            email="customer@example.com",
            password="testpass123"
        )

        self.store = Store.objects.create(
            name="Customer Store",
            slug="customer-store",
            owner=self.user
        )

        # Create page post type
        self.page_type = PostType.objects.create(
            name="Page",
            slug="page",
            store=self.store,
            is_public=True,
            is_hierarchical=True
        )

        # Create pages
        self.page = Post.objects.create(
            store=self.store,
            post_type=self.page_type,
            title="Customer Page",
            slug="customer-page",
            content="Customer page content",
            status="published",
            author=self.user
        )

        self.draft_page = Post.objects.create(
            store=self.store,
            post_type=self.page_type,
            title="Draft Page",
            slug="draft-page",
            content="Draft page content",
            status="draft",
            author=self.user
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_own_pages(self):
        """Test customer can list their own pages"""
        url = reverse('customer-pages-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 2)
        titles = [page['title'] for page in response.data]
        self.assertIn('Customer Page', titles)
        self.assertIn('Draft Page', titles)

    def test_create_page(self):
        """Test customer can create a page"""
        url = reverse('customer-pages-list')
        data = {
            "title": "New Customer Page",
            "slug": "new-customer-page",
            "content": "New page content",
            "status": "draft"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Customer Page')
        self.assertEqual(response.data['slug'], 'new-customer-page')
        self.assertEqual(response.data['author'], self.user.id)

    def test_retrieve_own_page(self):
        """Test customer can retrieve their own page"""
        url = reverse('customer-pages-detail', kwargs={'pk': self.page.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Customer Page')
        self.assertEqual(response.data['author'], self.user.id)

    def test_update_own_page(self):
        """Test customer can update their own page"""
        url = reverse('customer-pages-detail', kwargs={'pk': self.page.id})
        data = {
            "title": "Updated Customer Page",
            "content": "Updated content"
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Customer Page')
        self.assertEqual(response.data['content'], 'Updated content')

    def test_delete_own_page(self):
        """Test customer can delete their own page"""
        url = reverse('customer-pages-detail', kwargs={'pk': self.draft_page.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify it's deleted
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_publish_page(self):
        """Test customer can publish a page"""
        url = reverse('customer-pages-detail', kwargs={'pk': self.draft_page.id})
        publish_url = f"{url}publish/"
        
        response = self.client.post(publish_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'published')

    def test_unpublish_page(self):
        """Test customer can unpublish a page"""
        url = reverse('customer-pages-detail', kwargs={'pk': self.page.id})
        unpublish_url = f"{url}unpublish/"
        
        response = self.client.post(unpublish_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'draft')

    def test_page_revisions(self):
        """Test customer can view page revisions"""
        url = reverse('customer-pages-detail', kwargs={'pk': self.page.id})
        revisions_url = f"{url}revisions/"
        
        response = self.client.get(revisions_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_page_analytics(self):
        """Test customer can view page analytics"""
        url = reverse('customer-pages-detail', kwargs={'pk': self.page.id})
        analytics_url = f"{url}analytics/"
        
        response = self.client.get(analytics_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('page_id', response.data)
        self.assertIn('title', response.data)

    def test_cannot_access_other_store_pages(self):
        """Test customer cannot access pages from other stores"""
        from apps.stores.models import Store
        from apps.pages.models.pages import PostType, Post

        # Create another store and page
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123"
        )

        other_store = Store.objects.create(
            name="Other Store",
            slug="other-store",
            owner=other_user
        )

        other_page_type = PostType.objects.create(
            name="Page",
            slug="page",
            store=other_store
        )

        other_page = Post.objects.create(
            store=other_store,
            post_type=other_page_type,
            title="Other Page",
            slug="other-page",
            content="Other content",
            status="published",
            author=other_user
        )

        # Try to access other store's page
        url = reverse('customer-pages-detail', kwargs={'pk': other_page.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_customer_access(self):
        """Test unauthenticated customer cannot access customer endpoints"""
        self.client.force_authenticate(user=None)

        url = reverse('customer-pages-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_page_without_slug(self):
        """Test creating page without slug (should auto-generate)"""
        url = reverse('customer-pages-list')
        data = {
            "title": "Page Without Slug",
            "content": "Page content",
            "status": "draft"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Page Without Slug')
        self.assertIsNotNone(response.data['slug'])

    def test_update_page_status(self):
        """Test updating page status"""
        url = reverse('customer-pages-detail', kwargs={'pk': self.draft_page.id})
        data = {"status": "published"}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'published')

    def test_search_own_pages(self):
        """Test searching own pages"""
        url = reverse('customer-pages-list')
        response = self.client.get(url, {'search': 'customer'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Customer Page')

    def test_filter_own_pages_by_status(self):
        """Test filtering own pages by status"""
        url = reverse('customer-pages-list')
        response = self.client.get(url, {'status': 'published'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'published')

    def test_ordering_own_pages(self):
        """Test ordering own pages"""
        url = reverse('customer-pages-list')
        response = self.client.get(url, {'ordering': 'title'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], 'Customer Page')
        self.assertEqual(response.data[1]['title'], 'Draft Page')
