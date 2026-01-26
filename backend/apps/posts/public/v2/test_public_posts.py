"""
Public posts API tests - endpoint-focused only.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import json

User = get_user_model()


class PublicPostsAPITests(APITestCase):
    """Test public posts endpoints - read-only only."""

    def setUp(self):
        """Set up test data"""
        from apps.stores.models import Store
        from apps.posts.models import Post, PostType

        self.store = Store.objects.create(
            name="Test Store",
            slug="test-store",
            owner=None
        )

        # Create a post type
        self.post_type = PostType.objects.create(
            name="Blog Post",
            slug="blog-post",
            store=self.store,
            is_public=True
        )

        # Create a published post
        self.post = Post.objects.create(
            store=self.store,
            post_type=self.post_type,
            title="Test Post",
            slug="test-post",
            content="Test content",
            status="published"
        )

        # Create a draft post (should not be visible)
        self.draft_post = Post.objects.create(
            store=self.store,
            post_type=self.post_type,
            title="Draft Post",
            slug="draft-post",
            content="Draft content",
            status="draft"
        )

        self.client = APIClient()

    def test_list_published_posts(self):
        """Test listing published posts"""
        url = reverse('public-posts-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Post')

    def test_retrieve_published_post(self):
        """Test retrieving a specific published post"""
        url = reverse('public-posts-detail', kwargs={'pk': self.post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Post')
        self.assertEqual(response.data['content'], 'Test content')

    def test_draft_posts_not_visible(self):
        """Test that draft posts are not visible in public API"""
        url = reverse('public-posts-list')
        response = self.client.get(url)

        # Should only see the published post
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Post')

    def test_retrieve_draft_post(self):
        """Test that draft posts cannot be retrieved"""
        url = reverse('public-posts-detail', kwargs={'pk': self.draft_post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_search(self):
        """Test post search functionality"""
        url = reverse('public-posts-list')
        response = self.client.get(url, {'search': 'test'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_post_filter_by_type(self):
        """Test filtering posts by post type"""
        url = reverse('public-posts-list')
        response = self.client.get(url, {'post_type': 'blog-post'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_post_with_featured_image(self):
        """Test post with featured image"""
        from apps.mediafile.models import MediaFile
        
        # Create a media file
        media_file = MediaFile.objects.create(
            store=self.store,
            file_type="image",
            title="Test Image",
            alt_text="Test alt text"
        )
        
        # Update post with featured image
        self.post.featured_image = media_file
        self.post.save()

        url = reverse('public-posts-detail', kwargs={'pk': self.post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('featured_image', response.data)

    def test_post_with_categories(self):
        """Test post with categories"""
        from apps.posts.models import Taxonomy, Term
        
        # Create category taxonomy
        category_taxonomy = Taxonomy.objects.create(
            name="Categories",
            slug="categories",
            taxonomy_type="category",
            store=self.store
        )
        
        # Create category term
        category = Term.objects.create(
            name="Test Category",
            slug="test-category",
            taxonomy=category_taxonomy,
            store=self.store
        )
        
        # Add category to post
        self.post.categories.add(category_taxonomy)

        url = reverse('public-posts-detail', kwargs={'pk': self.post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('categories', response.data)

    def test_post_with_tags(self):
        """Test post with tags"""
        from apps.posts.models import Taxonomy, Term
        
        # Create tag taxonomy
        tag_taxonomy = Taxonomy.objects.create(
            name="Tags",
            slug="tags",
            taxonomy_type="tag",
            store=self.store
        )
        
        # Create tag term
        tag = Term.objects.create(
            name="test-tag",
            slug="test-tag",
            taxonomy=tag_taxonomy,
            store=self.store
        )
        
        # Add tag to post
        self.post.tags.add(tag)

        url = reverse('public-posts-detail', kwargs={'pk': self.post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tags', response.data)

    def test_post_seo_metadata(self):
        """Test post SEO metadata"""
        # Update post with SEO metadata
        self.post.meta_title = "SEO Title"
        self.post.meta_description = "SEO Description"
        self.post.meta_keywords = "seo,keywords"
        self.post.save()

        url = reverse('public-posts-detail', kwargs={'pk': self.post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['meta_title'], 'SEO Title')
        self.assertEqual(response.data['meta_description'], 'SEO Description')
        self.assertEqual(response.data['meta_keywords'], 'seo,keywords')
