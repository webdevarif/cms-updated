import time
from unittest.mock import patch

import pytest
from apps.analytics.services.search_service import SimpleSearchService
from apps.ecommerce.models.products import Product
from apps.posts.models import Post
from apps.stores.models import Store

from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class SimpleSearchServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass"
        )
        self.store = Store.objects.create(name="Test Store", owner=self.user)

        # Create a PostType for the test
        from apps.posts.models import PostType

        self.post_type = PostType.objects.create(
            name="Test Post Type", slug="test-post-type", store=self.store
        )

        # Create test data
        self.post1 = Post.objects.create(
            store=self.store,
            title="Test Post One",
            content="Content one",
            status="published",
            post_type=self.post_type,
        )
        self.post2 = Post.objects.create(
            store=self.store,
            title="Another Post",
            content="Content two",
            status="published",
            post_type=self.post_type,
        )
        self.product1 = Product.objects.create(
            store=self.store,
            title="Test Product",
            description="Product description",
            is_active=True,
        )

        # Create additional records for high-volume test
        for i in range(50):
            Post.objects.create(
                store=self.store,
                title=f"Post {i}",
                content=f"Content {i}",
                status="published",
                post_type=self.post_type,
            )

    def test_search_basic_query_returns_matches(self):
        results = SimpleSearchService.search(query="Test", store=self.store)
        self.assertEqual(results["total"], 2)  # post1 and product1
        self.assertEqual(len(results["results"]), 2)
        self.assertIn("Test Post One", [r["title"] for r in results["results"]])
        self.assertIn("Test Product", [r["title"] for r in results["results"]])

    def test_search_no_matches_returns_empty(self):
        results = SimpleSearchService.search(query="Nonexistent", store=self.store)
        self.assertEqual(results["total"], 0)
        self.assertEqual(len(results["results"]), 0)

    def test_search_pagination_limit_and_offset(self):
        results = SimpleSearchService.search(query="Post", store=self.store, limit=2, offset=0)
        self.assertEqual(len(results["results"]), 2)
        # Test offset
        results_offset = SimpleSearchService.search(
            query="Post", store=self.store, limit=2, offset=2
        )
        self.assertEqual(len(results_offset["results"]), 2)
        # Ensure different results
        self.assertNotEqual(
            [r["title"] for r in results["results"]],
            [r["title"] for r in results_offset["results"]],
        )

    def test_search_empty_or_whitespace_query(self):
        # Empty query
        results = SimpleSearchService.search(query="", store=self.store)
        self.assertEqual(results["total"], 0)
        self.assertEqual(len(results["results"]), 0)
        # Whitespace query
        results_whitespace = SimpleSearchService.search(query="   ", store=self.store)
        self.assertEqual(results_whitespace["total"], 0)
        self.assertEqual(len(results_whitespace["results"]), 0)

    @patch("apps.analytics.services.event_service.EventService.log_search")
    def test_search_triggers_event_service_log_search(self, mock_log_search):
        SimpleSearchService.search(query="Test", store=self.store)
        mock_log_search.assert_called_once()
        args, kwargs = mock_log_search.call_args
        self.assertEqual(args[0], "Test")  # query
        self.assertIsInstance(args[1], int)  # results_count
        self.assertIsInstance(args[2], int)  # duration_ms

    def test_high_volume_search_correctness(self):
        start_time = time.time()
        results = SimpleSearchService.search(query="Post", store=self.store, limit=20, offset=0)
        duration_ms = int((time.time() - start_time) * 1000)
        # Should find many posts (including seeded ones)
        self.assertGreater(results["total"], 50)
        self.assertEqual(len(results["results"]), 20)  # limited
        # Reasonable time (under 1 second for this test scale)
        self.assertLess(duration_ms, 1000)
        # Verify all results contain "Post" in title
        for result in results["results"]:
            self.assertIn("Post", result["title"])

    def test_search_with_content_types_filter(self):
        results_posts_only = SimpleSearchService.search(
            query="Test", store=self.store, content_types=["post"]
        )
        self.assertEqual(results_posts_only["total"], 1)  # Only post1
        self.assertEqual(len(results_posts_only["results"]), 1)
        self.assertEqual(results_posts_only["results"][0]["type"], "post")

        results_products_only = SimpleSearchService.search(
            query="Test", store=self.store, content_types=["product"]
        )
        self.assertEqual(results_products_only["total"], 1)  # Only product1
        self.assertEqual(len(results_products_only["results"]), 1)
        self.assertEqual(results_products_only["results"][0]["type"], "product")
