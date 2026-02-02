"""
Customer posts API tests - endpoint-focused only.
"""

import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class CustomerPostsAPITests(APITestCase):
    """Test customer posts endpoints"""

    def setUp(self):
        """Set up test data"""
        from apps.posts.models import Post, PostType
        from apps.stores.models import Store

        self.user = User.objects.create_user(email="customer@example.com", password="testpass123")

        self.store = Store.objects.create(
            name="Customer Store", slug="customer-store", owner=self.user
        )

        # Create post types
        self.blog_type = PostType.objects.create(
            name="Blog Post", slug="blog-post", store=self.store, is_public=True
        )

        self.private_type = PostType.objects.create(
            name="Private Post", slug="private-post", store=self.store, is_public=False
        )

        # Create posts
        self.public_post = Post.objects.create(
            store=self.store,
            post_type=self.blog_type,
            title="Public Post",
            slug="public-post",
            content="Public content",
            status="published",
            author=self.user,
        )

        self.private_post = Post.objects.create(
            store=self.store,
            post_type=self.private_type,
            title="Private Post",
            slug="private-post",
            content="Private content",
            status="published",
            author=self.user,
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_customer_posts(self):
        """Test customer can list their posts"""
        url = reverse("customer-posts-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_customer_post(self):
        """Test customer can retrieve their post"""
        url = reverse("customer-posts-detail", kwargs={"pk": self.public_post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Public Post")

    def test_create_post(self):
        """Test customer can create a post"""
        url = reverse("customer-posts-list")
        data = {
            "title": "New Customer Post",
            "slug": "new-customer-post",
            "content": "New post content",
            "post_type": self.blog_type.id,
            "status": "draft",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Customer Post")
        self.assertEqual(response.data["author"], self.user.id)

    def test_update_post(self):
        """Test customer can update their post"""
        url = reverse("customer-posts-detail", kwargs={"pk": self.public_post.id})
        data = {"title": "Updated Post", "content": "Updated content"}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Post")

    def test_delete_post(self):
        """Test customer can delete their post"""
        url = reverse("customer-posts-detail", kwargs={"pk": self.public_post.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_publish_post(self):
        """Test customer can publish a post"""
        # Create a draft post
        draft_post = Post.objects.create(
            store=self.store,
            post_type=self.blog_type,
            title="Draft Post",
            slug="draft-post",
            content="Draft content",
            status="draft",
            author=self.user,
        )

        url = reverse("customer-posts-publish", kwargs={"pk": draft_post.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "published")

    def test_unschedule_post(self):
        """Test customer can unschedule a post"""
        # Create a scheduled post
        scheduled_post = Post.objects.create(
            store=self.store,
            post_type=self.blog_type,
            title="Scheduled Post",
            slug="scheduled-post",
            content="Scheduled content",
            status="scheduled",
            author=self.user,
        )

        url = reverse("customer-posts-unschedule", kwargs={"pk": scheduled_post.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "draft")

    def test_post_revisions(self):
        """Test customer can view post revisions"""
        url = reverse("customer-posts-revisions", kwargs={"pk": self.public_post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_post_analytics(self):
        """Test customer can view post analytics"""
        url = reverse("customer-posts-analytics", kwargs={"pk": self.public_post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_cannot_access_other_store_posts(self):
        """Test customer cannot access posts from other stores"""
        from apps.posts.models import Post, PostType
        from apps.stores.models import Store

        # Create another store and post
        other_user = User.objects.create_user(email="other@example.com", password="testpass123")

        other_store = Store.objects.create(name="Other Store", slug="other-store", owner=other_user)

        other_post_type = PostType.objects.create(
            name="Other Blog", slug="other-blog", store=other_store
        )

        other_post = Post.objects.create(
            store=other_store,
            post_type=other_post_type,
            title="Other Post",
            slug="other-post",
            content="Other content",
            status="published",
            author=other_user,
        )

        # Try to access other store's post
        url = reverse("customer-posts-detail", kwargs={"pk": other_post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_customer_access(self):
        """Test unauthenticated customer cannot access customer endpoints"""
        self.client.force_authenticate(user=None)

        url = reverse("customer-posts-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_with_featured_image_upload(self):
        """Test customer can upload featured image for post"""
        url = reverse("customer-posts-detail", kwargs={"pk": self.public_post.id})

        # Mock file upload
        from django.core.files.uploadedfile import SimpleUploadedFile

        test_image = SimpleUploadedFile("test.jpg", b"fake_image_data", content_type="image/jpeg")

        data = {"featured_image": test_image}

        response = self.client.patch(url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("featured_image", response.data)
