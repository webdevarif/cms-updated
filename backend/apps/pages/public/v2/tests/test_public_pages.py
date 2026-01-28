"""
Public pages API tests - endpoint-focused only.
"""
import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class PublicPagesAPITests(APITestCase):
    """Test public pages endpoints - read-only only."""

    def setUp(self):
        """Set up test data"""
        from apps.pages.models.pages import Post, PostType
        from apps.stores.models import Store

        self.store = Store.objects.create(name="Test Store", slug="test-store", owner=None)

        # Create a page post type
        self.page_type = PostType.objects.create(
            name="Page", slug="page", store=self.store, is_public=True, is_hierarchical=True
        )

        # Create a published page
        self.page = Post.objects.create(
            store=self.store,
            post_type=self.page_type,
            title="Test Page",
            slug="test-page",
            content="Test page content",
            status="published",
        )

        # Create a draft page (should not be visible)
        self.draft_page = Post.objects.create(
            store=self.store,
            post_type=self.page_type,
            title="Draft Page",
            slug="draft-page",
            content="Draft page content",
            status="draft",
        )

        self.client = APIClient()

    def test_list_published_pages(self):
        """Test listing published pages"""
        url = reverse("public-pages-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Page")
        self.assertEqual(response.data[0]["slug"], "test-page")

    def test_retrieve_page_by_id(self):
        """Test retrieving a page by ID"""
        url = reverse("public-pages-detail", kwargs={"pk": self.page.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Page")
        self.assertEqual(response.data["content"], "Test page content")
        self.assertEqual(response.data["slug"], "test-page")

    def test_retrieve_page_by_slug(self):
        """Test retrieving a page by slug"""
        url = reverse("public-pages-detail", kwargs={"pk": self.page.id})
        # Test the custom slug action
        slug_url = f"/api/public/pages/slug/test-page/"
        response = self.client.get(slug_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Page")
        self.assertEqual(response.data["slug"], "test-page")

    def test_draft_pages_not_visible(self):
        """Test that draft pages are not visible in public API"""
        url = reverse("public-pages-list")
        response = self.client.get(url)

        # Should only see the published page
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Page")

    def test_retrieve_draft_page_by_id(self):
        """Test that draft pages cannot be retrieved by ID"""
        url = reverse("public-pages-detail", kwargs={"pk": self.draft_page.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_draft_page_by_slug(self):
        """Test that draft pages cannot be retrieved by slug"""
        slug_url = f"/api/public/pages/slug/draft-page/"
        response = self.client.get(slug_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_nonexistent_page_by_id(self):
        """Test retrieving non-existent page by ID"""
        url = reverse("public-pages-detail", kwargs={"pk": 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_nonexistent_page_by_slug(self):
        """Test retrieving non-existent page by slug"""
        slug_url = f"/api/public/pages/slug/nonexistent/"
        response = self.client.get(slug_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_page_search(self):
        """Test page search functionality"""
        url = reverse("public-pages-list")
        response = self.client.get(url, {"search": "test"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Page")

    def test_page_ordering(self):
        """Test page ordering"""
        # Create another page
        Post.objects.create(
            store=self.store,
            post_type=self.page_type,
            title="Another Page",
            slug="another-page",
            content="Another content",
            status="published",
        )

        url = reverse("public-pages-list")
        response = self.client.get(url, {"ordering": "title"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["title"], "Another Page")
        self.assertEqual(response.data[1]["title"], "Test Page")

    def test_page_filtering(self):
        """Test page filtering"""
        url = reverse("public-pages-list")
        response = self.client.get(url, {"status": "published"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], "published")

    def test_featured_image_field(self):
        """Test featured image field in response"""
        url = reverse("public-pages-detail", kwargs={"pk": self.page.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("featured_image", response.data)
        # Should be None since no image is set
        self.assertIsNone(response.data["featured_image"])

    def test_seo_fields(self):
        """Test SEO fields in response"""
        # Update page with SEO data
        self.page.meta_title = "SEO Title"
        self.page.meta_description = "SEO Description"
        self.page.meta_keywords = "seo,keywords"
        self.page.save()

        url = reverse("public-pages-detail", kwargs={"pk": self.page.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["meta_title"], "SEO Title")
        self.assertEqual(response.data["meta_description"], "SEO Description")
        self.assertEqual(response.data["meta_keywords"], "seo,keywords")

    def test_url_field(self):
        """Test URL field in response"""
        url = reverse("public-pages-detail", kwargs={"pk": self.page.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("url", response.data)
        # Should contain the slug-based URL
        self.assertIn("test-page", response.data["url"])

    def test_read_only_serializer_fields(self):
        """Test that serializer fields are read-only"""
        url = reverse("public-pages-detail", kwargs={"pk": self.page.id})

        # Try to update via POST (should fail)
        response = self.client.post(url, {"title": "Updated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Try to update via PATCH (should fail)
        response = self.client.patch(url, {"title": "Updated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Try to update via PUT (should fail)
        response = self.client.put(url, {"title": "Updated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Try to delete (should fail)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
