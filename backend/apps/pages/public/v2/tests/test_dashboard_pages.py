"""
Dashboard pages API tests - endpoint-focused only.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import json

User = get_user_model()


class DashboardPagesAPITests(APITestCase):
    """Test dashboard pages endpoints"""

    def setUp(self):
        """Set up test data"""
        from apps.stores.models import Store
        from apps.pages.models.pages import Post, PostType, Taxonomy, Term

        self.user = User.objects.create_user(
            email="admin@example.com",
            password="testpass123"
        )

        self.store = Store.objects.create(
            name="Admin Store",
            slug="admin-store",
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

        # Create test page
        self.page = Post.objects.create(
            store=self.store,
            post_type=self.page_type,
            title="Dashboard Page",
            slug="dashboard-page",
            content="Dashboard content",
            status="published",
            author=self.user
        )

        # Create taxonomy for pages
        self.page_taxonomy = Taxonomy.objects.create(
            name="Page Categories",
            slug="page-categories",
            taxonomy_type="category",
            store=self.store
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_all_pages(self):
        """Test admin can list all pages in store"""
        url = reverse('dashboard-pages-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Dashboard Page')

    def test_create_page_admin(self):
        """Test admin can create a page"""
        url = reverse('dashboard-pages-list')
        data = {
            "title": "New Admin Page",
            "slug": "new-admin-page",
            "content": "New admin content",
            "status": "draft",
            "meta_title": "SEO Title",
            "meta_description": "SEO Description"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Admin Page')
        self.assertEqual(response.data['slug'], 'new-admin-page')

    def test_update_any_page(self):
        """Test admin can update any page"""
        url = reverse('dashboard-pages-detail', kwargs={'pk': self.page.id})
        data = {
            "title": "Updated Admin Page",
            "content": "Updated content",
            "status": "published"
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Admin Page')

    def test_delete_any_page(self):
        """Test admin can delete any page"""
        url = reverse('dashboard-pages-detail', kwargs={'pk': self.page.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_publish_page(self):
        """Test admin can publish a page"""
        # Create a draft page
        draft_page = Post.objects.create(
            store=self.store,
            post_type=self.page_type,
            title="Draft Page",
            slug="draft-page",
            content="Draft content",
            status="draft",
            author=self.user
        )

        url = reverse('dashboard-pages-detail', kwargs={'pk': draft_page.id})
        publish_url = f"{url}publish/"
        
        response = self.client.post(publish_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'published')

    def test_bulk_actions(self):
        """Test bulk actions on pages"""
        # Create another page for bulk action
        page2 = Post.objects.create(
            store=self.store,
            post_type=self.page_type,
            title="Second Page",
            slug="second-page",
            content="Second content",
            status="draft",
            author=self.user
        )

        url = reverse('dashboard-pages-bulk-action')
        data = {
            "action": "publish",
            "page_ids": [self.page.id, page2.id]
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], 2)

    def test_page_revisions(self):
        """Test page revisions management"""
        url = reverse('dashboard-pages-detail', kwargs={'pk': self.page.id})
        revisions_url = f"{url}revisions/"
        
        response = self.client.get(revisions_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_restore_revision(self):
        """Test restoring page revision"""
        from apps.pages.models.pages import PostRevision
        
        # Create a revision
        revision = PostRevision.objects.create(
            post=self.page,
            user=self.user,
            title="Old Title",
            content="Old content",
            revision_number=1
        )

        url = reverse('dashboard-pages-detail', kwargs={'pk': self.page.id})
        restore_url = f"{url}restore-revision/"
        
        data = {"revision_id": revision.id}
        response = self.client.post(restore_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Old Title')

    def test_analytics_endpoint(self):
        """Test analytics endpoint"""
        url = reverse('dashboard-pages-analytics')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_pages', response.data)
        self.assertIn('published_pages', response.data)

    def test_reports_endpoint(self):
        """Test reports endpoint"""
        url = reverse('dashboard-pages-reports')
        response = self.client.get(url, {'period': '30d'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('period', response.data)

    def test_post_type_management(self):
        """Test post type CRUD operations"""
        # Create post type
        url = reverse('dashboard-post-types-list')
        data = {
            "name": "Custom Page Type",
            "slug": "custom-page",
            "is_public": True,
            "is_hierarchical": True
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Custom Page Type')

        # Update post type
        post_type_id = response.data['id']
        update_url = reverse('dashboard-post-types-detail', kwargs={'pk': post_type_id})
        update_data = {"name": "Updated Page Type"}
        
        response = self.client.patch(update_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Page Type')

    def test_taxonomy_management(self):
        """Test taxonomy CRUD operations"""
        # Create taxonomy
        url = reverse('dashboard-taxonomies-list')
        data = {
            "name": "Page Tags",
            "slug": "page-tags",
            "taxonomy_type": "tag",
            "description": "Page tags for categorization"
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Page Tags')

        # Create term
        taxonomy_id = response.data['id']
        term_url = reverse('dashboard-terms-list')
        term_data = {
            "name": "Test Tag",
            "slug": "test-tag",
            "taxonomy": taxonomy_id,
            "description": "Test tag description"
        }

        response = self.client.post(term_url, term_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Tag')

    def test_search_pages(self):
        """Test page search functionality"""
        url = reverse('dashboard-pages-list')
        response = self.client.get(url, {'search': 'dashboard'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Dashboard Page')

    def test_filter_pages_by_status(self):
        """Test filtering pages by status"""
        url = reverse('dashboard-pages-list')
        response = self.client.get(url, {'status': 'published'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'published')

    def test_ordering_pages(self):
        """Test page ordering"""
        # Create another page
        Post.objects.create(
            store=self.store,
            post_type=self.page_type,
            title="AAA Page",
            slug="aaa-page",
            content="AAA content",
            status="published",
            author=self.user
        )

        url = reverse('dashboard-pages-list')
        response = self.client.get(url, {'ordering': 'title'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], 'AAA Page')
        self.assertEqual(response.data[1]['title'], 'Dashboard Page')

    def test_unauthenticated_access(self):
        """Test unauthenticated user cannot access dashboard"""
        self.client.force_authenticate(user=None)

        url = reverse('dashboard-pages-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_store_owner_access(self):
        """Test non-store owner cannot access dashboard"""
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123"
        )

        self.client.force_authenticate(user=other_user)

        url = reverse('dashboard-pages-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_page_with_categories_and_tags(self):
        """Test page with categories and tags"""
        # Create tag taxonomy
        tag_taxonomy = Taxonomy.objects.create(
            name="Tags",
            slug="tags",
            taxonomy_type="tag",
            store=self.store
        )

        # Create terms
        category_term = Term.objects.create(
            name="Test Category",
            slug="test-category",
            taxonomy=self.page_taxonomy,
            store=self.store
        )

        tag_term = Term.objects.create(
            name="test-tag",
            slug="test-tag",
            taxonomy=tag_taxonomy,
            store=self.store
        )

        # Add to page
        self.page.categories.add(self.page_taxonomy)
        self.page.tags.add(tag_term)

        url = reverse('dashboard-pages-detail', kwargs={'pk': self.page.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('categories', response.data)
        self.assertIn('tags', response.data)
        self.assertEqual(len(response.data['categories']), 1)
        self.assertEqual(len(response.data['tags']), 1)

    def test_custom_fields(self):
        """Test custom fields support"""
        # Update page with custom fields
        self.page.custom_fields = {
            "custom_field_1": "value1",
            "custom_field_2": "value2"
        }
        self.page.save()

        url = reverse('dashboard-pages-detail', kwargs={'pk': self.page.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('custom_fields', response.data)
        self.assertEqual(response.data['custom_fields']['custom_field_1'], 'value1')
