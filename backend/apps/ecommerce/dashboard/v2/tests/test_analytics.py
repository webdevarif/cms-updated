"""
Tests for dashboard ecommerce API - analytics.
"""

from apps.accounts.models import User
from apps.ecommerce.models import Product, ProductCategory, Review
from core.models import Store
from rest_framework import status
from rest_framework.test import APITestCase

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone


class ReviewAnalyticsTests(APITestCase):
    """Test review analytics functionality"""

    def setUp(self):
        """Set up test data"""
        self.store = Store.objects.create(
            name="Test Store", slug="test-store", email="test@test.com"
        )

        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            is_staff=True,
            store=self.store,
        )

        self.category = ProductCategory.objects.create(
            store=self.store, name="Test Category", slug="test-category"
        )

        self.product = Product.objects.create(
            title="Test Product",
            slug="test-product",
            description="Test description",
            price=29.99,
            category=self.category,
            store=self.store,
            created_by=self.user,
        )

        # Create test reviews
        self.review1 = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            title="Great product!",
            content="This product is amazing",
            is_approved=True,
            verified_purchase=True,
        )

        self.review2 = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=4,
            title="Good product",
            content="Pretty good overall",
            moderation_status="pending",
        )

        self.review3 = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=3,
            title="Average product",
            content="It's okay",
            is_approved=True,
            is_featured=True,
        )

        self.client.force_authenticate(user=self.user)

    def test_analytics_basic(self):
        """Test basic analytics functionality"""
        url = reverse("ecommerce_v2:dashboard-reviews-analytics")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn("total_reviews", data)
        self.assertIn("approved_reviews", data)
        self.assertIn("pending_reviews", data)
        self.assertIn("average_rating", data)
        self.assertIn("top_reviewers", data)
        self.assertIn("top_products", data)
        self.assertIn("moderation_stats", data)
        self.assertIn("rating_trends", data)
        self.assertIn("time_range", data)

        # Check that counts are correct
        self.assertEqual(data["total_reviews"], 3)
        self.assertEqual(data["approved_reviews"], 2)
        self.assertEqual(data["pending_reviews"], 1)
        self.assertEqual(data["average_rating"], 4.0)  # (5+3)/2

    def test_analytics_with_date_filter(self):
        """Test analytics with custom date filtering"""
        url = reverse("ecommerce_v2:dashboard-reviews-analytics")

        start_date = (timezone.now() - timezone.timedelta(days=7)).isoformat()
        end_date = timezone.now().isoformat()

        response = self.client.get(url, {"start_date": start_date, "end_date": end_date})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn("time_range", data)
        self.assertTrue(data["time_range"]["has_custom_range"])

    def test_analytics_approved_only(self):
        """Test analytics with approved_only filter"""
        url = reverse("ecommerce_v2:dashboard-reviews-analytics")

        response = self.client.get(url, {"approved_only": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        # Should include average rating even with approved_only
        self.assertIn("average_rating", data)

    def test_analytics_top_reviewers(self):
        """Test top reviewers analytics"""
        url = reverse("ecommerce_v2:dashboard-reviews-analytics")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn("top_reviewers", data)
        self.assertIsInstance(data["top_reviewers"], list)

        # Should have our test user
        reviewer_usernames = [r["user__username"] for r in data["top_reviewers"]]
        self.assertIn("testuser", reviewer_usernames)

    def test_analytics_top_products(self):
        """Test top products by reviews analytics"""
        url = reverse("ecommerce_v2:dashboard-reviews-analytics")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn("top_products", data)
        self.assertIsInstance(data["top_products"], list)

        # Should have our test product
        product_titles = [p["product__title"] for p in data["top_products"]]
        self.assertIn("Test Product", product_titles)

    def test_analytics_moderation_stats(self):
        """Test moderation statistics"""
        url = reverse("ecommerce_v2:dashboard-reviews-analytics")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn("moderation_stats", data)

        mod_stats = data["moderation_stats"]
        self.assertIn("pending_review", mod_stats)
        self.assertIn("recently_approved", mod_stats)
        self.assertIn("recently_rejected", mod_stats)
        self.assertIn("featured_reviews", mod_stats)

        # Check featured reviews count
        self.assertEqual(mod_stats["featured_reviews"], 1)

    def test_analytics_rating_distribution(self):
        """Test rating distribution analytics"""
        url = reverse("ecommerce_v2:dashboard-reviews-analytics")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn("rating_distribution", data)

        rating_dist = data["rating_distribution"]
        self.assertEqual(rating_dist[5], 1)  # One 5-star review
        self.assertEqual(rating_dist[4], 0)  # No 4-star reviews (pending)
        self.assertEqual(rating_dist[3], 1)  # One 3-star review

    def test_analytics_rating_trends(self):
        """Test rating trends analytics"""
        url = reverse("ecommerce_v2:dashboard-reviews-analytics")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn("rating_trends", data)
        self.assertIsInstance(data["rating_trends"], list)
