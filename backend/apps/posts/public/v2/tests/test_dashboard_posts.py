"""
Dashboard posts API tests - endpoint-focused only.
"""

import json

from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class DashboardPostsAPITests(APITestCase):
    """Test dashboard posts endpoints"""

    def setUp(self):
        """Set up test data"""
        from apps.posts.models import Post, PostType, Taxonomy, Term
        from apps.stores.models import Store

        self.user = User.objects.create_user(email="admin@example.com", password="testpass123")

        self.store = Store.objects.create(name="Admin Store", slug="admin-store", owner=self.user)

        # Create post types
        self.blog_type = PostType.objects.create(
            name="Blog Post", slug="blog-post", store=self.store, is_public=True
        )

        self.page_type = PostType.objects.create(
            name="Page",
            slug="page",
            store=self.store,
            is_public=True,
            is_hierarchical=True,
        )

        # Create test post
        self.post = Post.objects.create(
            store=self.store,
            post_type=self.blog_type,
            title="Dashboard Post",
            slug="dashboard-post",
            content="Dashboard content",
            status="published",
            author=self.user,
        )

        # Create taxonomy
        self.category_taxonomy = Taxonomy.objects.create(
            name="Categories",
            slug="categories",
            taxonomy_type="category",
            store=self.store,
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_post(self):
        """Test creating a new post"""
        url = reverse("dashboard-posts-list")
        data = {
            "title": "New Admin Post",
            "slug": "new-admin-post",
            "content": "New admin content",
            "post_type": self.blog_type.id,
            "status": "draft",
            "meta_title": "SEO Title",
            "meta_description": "SEO Description",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Admin Post")
        self.assertEqual(response.data["author"], self.user.id)

    def test_update_post(self):
        """Test updating an existing post"""
        url = reverse("dashboard-posts-detail", kwargs={"pk": self.post.id})
        data = {
            "title": "Updated Admin Post",
            "content": "Updated content",
            "status": "published",
        }

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Admin Post")

    def test_delete_post(self):
        """Test deleting a post"""
        url = reverse("dashboard-posts-detail", kwargs={"pk": self.post.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_posts(self):
        """Test listing all posts"""
        url = reverse("dashboard-posts-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_bulk_post_actions(self):
        """Test bulk post actions"""
        # Create another post for bulk action
        post2 = Post.objects.create(
            store=self.store,
            post_type=self.blog_type,
            title="Second Post",
            slug="second-post",
            content="Second content",
            status="draft",
            author=self.user,
        )

        url = reverse("dashboard-posts-bulk-action")
        data = {"action": "publish", "post_ids": [self.post.id, post2.id]}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post_type(self):
        """Test creating a new post type"""
        url = reverse("dashboard-post-types-list")
        data = {
            "name": "News Article",
            "slug": "news-article",
            "is_public": True,
            "supports_comments": True,
            "supports_featured_image": True,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "News Article")

    def test_update_post_type(self):
        """Test updating a post type"""
        url = reverse("dashboard-post-types-detail", kwargs={"pk": self.blog_type.id})
        data = {"name": "Updated Blog Post", "supports_comments": False}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Blog Post")

    def test_delete_post_type(self):
        """Test deleting a post type"""
        # Create a deletable post type
        deletable_type = PostType.objects.create(
            name="Deletable Type",
            slug="deletable-type",
            store=self.store,
            is_deletable=True,
        )

        url = reverse("dashboard-post-types-detail", kwargs={"pk": deletable_type.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_taxonomy(self):
        """Test creating a new taxonomy"""
        url = reverse("dashboard-taxonomies-list")
        data = {
            "name": "Tags",
            "slug": "tags",
            "taxonomy_type": "tag",
            "description": "Post tags",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Tags")

    def test_create_term(self):
        """Test creating a new term"""
        url = reverse("dashboard-terms-list")
        data = {
            "name": "Test Tag",
            "slug": "test-tag",
            "taxonomy": self.category_taxonomy.id,
            "description": "Test tag description",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Test Tag")

    def test_post_analytics(self):
        """Test post analytics"""
        url = reverse("dashboard-posts-analytics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_reports(self):
        """Test post reports"""
        url = reverse("dashboard-posts-reports")
        response = self.client.get(url, {"period": "30d"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_search_admin(self):
        """Test post search in admin"""
        url = reverse("dashboard-posts-list")
        response = self.client.get(url, {"search": "dashboard"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_post_filter_by_status(self):
        """Test filtering posts by status"""
        url = reverse("dashboard-posts-list")
        response = self.client.get(url, {"status": "published"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_post_filter_by_type(self):
        """Test filtering posts by post type"""
        url = reverse("dashboard-posts-list")
        response = self.client.get(url, {"post_type": self.blog_type.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_post_revisions_management(self):
        """Test post revisions management"""
        url = reverse("dashboard-posts-revisions", kwargs={"pk": self.post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_restore_post_revision(self):
        """Test restoring a post revision"""
        from apps.posts.models import PostRevision

        # Create a revision
        revision = PostRevision.objects.create(
            post=self.post,
            user=self.user,
            title="Old Title",
            content="Old content",
            revision_number=1,
        )

        url = reverse("dashboard-posts-restore-revision", kwargs={"pk": self.post.id})
        data = {"revision_id": revision.id}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_admin_access(self):
        """Test unauthenticated user cannot access dashboard"""
        self.client.force_authenticate(user=None)

        url = reverse("dashboard-posts-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_store_owner_admin_access(self):
        """Test non-store owner cannot access dashboard"""
        other_user = User.objects.create_user(email="other@example.com", password="testpass123")

        self.client.force_authenticate(user=other_user)

        url = reverse("dashboard-posts-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
