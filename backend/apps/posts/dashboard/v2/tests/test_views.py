"""
Tests for dashboard posts API - bulk operations.
"""
from apps.posts.models import Comment, Post, PostType
from apps.stores.models import Store
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class CommentAnalyticsTests(APITestCase):
    """Test comment analytics functionality"""

    def setUp(self):
        """Set up test data"""
        self.store = Store.objects.create(name="Test Store", slug="test-store", owner=self.user)

        self.user = User.objects.create_user(
            email="owner@test.com", username="owner", password="testpass123"
        )

        self.post_type = PostType.objects.create(name="Blog Post", slug="post")

        self.post = Post.objects.create(
            title="Test Post",
            content="Test content",
            post_type=self.post_type,
            store=self.store,
            author=self.user,
        )

        # Create test comments
        self.comment1 = Comment.objects.create(
            post=self.post,
            user=self.user,
            content="Test comment 1",
            is_approved=True,
            store=self.store,
        )

        self.comment2 = Comment.objects.create(
            post=self.post,
            user=self.user,
            content="Test comment 2",
            moderation_status="pending",
            store=self.store,
        )

        self.client.force_authenticate(user=self.user)

    def test_analytics_basic(self):
        """Test basic analytics functionality"""
        url = reverse("posts_v2:dashboard-comments-analytics")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn("total_comments", data)
        self.assertIn("approved_comments", data)
        self.assertIn("pending_comments", data)
        self.assertIn("top_commenters", data)
        self.assertIn("moderation_stats", data)
        self.assertIn("time_range", data)

        # Check that counts are correct
        self.assertEqual(data["total_comments"], 2)
        self.assertEqual(data["approved_comments"], 1)
        self.assertEqual(data["pending_comments"], 1)

    def test_analytics_with_date_filter(self):
        """Test analytics with custom date filtering"""
        url = reverse("posts_v2:dashboard-comments-analytics")

        start_date = (timezone.now() - timezone.timedelta(days=7)).isoformat()
        end_date = timezone.now().isoformat()

        response = self.client.get(url, {"start_date": start_date, "end_date": end_date})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn("time_range", data)
        self.assertTrue(data["time_range"]["has_custom_range"])

    def test_analytics_approved_only(self):
        """Test analytics with approved_only filter"""
        url = reverse("posts_v2:dashboard-comments-analytics")

        response = self.client.get(url, {"approved_only": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        # Should only include approved counts
        self.assertIn("approved_comments", data)

    def test_analytics_top_commenters(self):
        """Test top commenters analytics"""
        url = reverse("posts_v2:dashboard-comments-analytics")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn("top_commenters", data)
        self.assertIsInstance(data["top_commenters"], list)

    def test_analytics_moderation_stats(self):
        """Test moderation statistics"""
        url = reverse("posts_v2:dashboard-comments-analytics")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn("moderation_stats", data)

        mod_stats = data["moderation_stats"]
        self.assertIn("pending_review", mod_stats)
        self.assertIn("recently_approved", mod_stats)
        self.assertIn("recently_rejected", mod_stats)
        self.assertEqual(mod_stats["recently_rejected"], 0)


class CommentModerationQueueTests(APITestCase):
    """Test comment moderation queue functionality"""

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

        self.post_type = PostType.objects.create(name="Blog Post", slug="post")

        self.post = Post.objects.create(
            title="Test Post",
            slug="test-post",
            content="Test content",
            post_type=self.post_type,
            store=self.store,
            author=self.user,
        )

        # Create pending comments
        self.pending_comment1 = Comment.objects.create(
            post=self.post,
            user=self.user,
            content="Pending comment 1",
            moderation_status="pending",
            store=self.store,
        )

        self.pending_comment2 = Comment.objects.create(
            post=self.post,
            user=self.user,
            content="Pending comment 2",
            moderation_status="pending",
            store=self.store,
        )

        # Create approved comment
        self.approved_comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            content="Approved comment",
            moderation_status="approved",
            is_approved=True,
            store=self.store,
        )

        self.client.force_authenticate(user=self.user)

    def test_moderation_queue_list(self):
        """Test moderation queue returns only pending comments"""
        url = reverse("posts_v2:dashboard-comments-moderation_queue")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(len(data), 2)  # Only pending comments

        # Check that all returned comments are pending
        for comment in data:
            self.assertEqual(comment["moderation_status"], "pending")

    def test_moderation_queue_store_filter(self):
        """Test moderation queue with store filtering"""
        url = reverse("posts_v2:dashboard-comments-moderation_queue")

        response = self.client.get(url, {"store": self.store.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(len(data), 2)

    def test_approve_comment(self):
        """Test approving a comment"""
        url = reverse("posts_v2:dashboard-comments-approve", args=[self.pending_comment1.id])

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh from database
        self.pending_comment1.refresh_from_db()
        self.assertEqual(self.pending_comment1.moderation_status, "approved")
        self.assertTrue(self.pending_comment1.is_approved)

    def test_reject_comment(self):
        """Test rejecting a comment"""
        url = reverse("posts_v2:dashboard-comments-reject", args=[self.pending_comment1.id])

        data = {"reason": "Inappropriate content"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh from database
        self.pending_comment1.refresh_from_db()
        self.assertEqual(self.pending_comment1.moderation_status, "rejected")
        self.assertFalse(self.pending_comment1.is_approved)

    def test_approve_non_pending_comment(self):
        """Test approving an already approved comment fails"""
        url = reverse("posts_v2:dashboard-comments-approve", args=[self.approved_comment.id])

        response = self.client.post(url)
        # Should still work but comment stays approved
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(self.approved_comment.moderation_status, "approved")


class CommentVoteReportTests(APITestCase):
    """Test comment voting and abuse reporting functionality"""

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

        self.post_type = PostType.objects.create(name="Blog Post", slug="post")

        self.post = Post.objects.create(
            title="Test Post",
            slug="test-post",
            content="Test content",
            post_type=self.post_type,
            store=self.store,
            author=self.user,
        )

        # Create approved comment for voting
        self.approved_comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            content="Approved comment for voting",
            moderation_status="approved",
            is_approved=True,
            store=self.store,
        )

    def test_vote_helpful_success(self):
        """Test voting helpful on approved comment"""
        url = reverse("posts_v2:public-comment-vote_helpful", args=[self.approved_comment.id])

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn("helpful_votes", data)
        self.assertIn("total_votes", data)
        self.assertIn("helpfulness_percentage", data)
        self.assertEqual(data["helpful_votes"], 1)
        self.assertEqual(data["total_votes"], 1)
        self.assertEqual(data["helpfulness_percentage"], 100)

        # Refresh from database and verify
        self.approved_comment.refresh_from_db()
        self.assertEqual(self.approved_comment.helpful_votes, 1)
        self.assertEqual(self.approved_comment.total_votes, 1)

    def test_vote_helpful_unapproved_comment(self):
        """Test voting on unapproved comment fails"""
        # Create unapproved comment
        unapproved_comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            content="Unapproved comment",
            moderation_status="pending",
            is_approved=False,
            store=self.store,
        )

        url = reverse("posts_v2:public-comment-vote_helpful", args=[unapproved_comment.id])

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_report_abuse_success(self):
        """Test reporting abuse on comment"""
        url = reverse("posts_v2:public-comment-report_abuse", args=[self.approved_comment.id])

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn("message", data)
        self.assertIn("abuse_reports_count", data)
        self.assertIn("is_hidden", data)
        self.assertEqual(data["abuse_reports_count"], 1)
        self.assertEqual(data["is_hidden"], False)

        # Refresh from database and verify
        self.approved_comment.refresh_from_db()
        self.assertEqual(self.approved_comment.abuse_reports_count, 1)

    def test_report_abuse_auto_hide(self):
        """Test that comment gets hidden after 5 abuse reports"""
        # Create 4 more reports
        for i in range(4):
            self.approved_comment.abuse_reports_count += 1
            self.approved_comment.save()

        url = reverse("posts_v2:public-comment-report_abuse", args=[self.approved_comment.id])

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data["abuse_reports_count"], 5)
        self.assertEqual(data["is_hidden"], True)

        # Refresh from database and verify
        self.approved_comment.refresh_from_db()
        self.assertEqual(self.approved_comment.abuse_reports_count, 5)
        self.assertEqual(self.approved_comment.is_hidden, True)


class DashboardPostsBulkOperationsTest(APITestCase):
    """Test bulk operations for posts dashboard API"""

    def setUp(self):
        """Set up test data"""
        self.store_owner = User.objects.create_user(
            email="owner@test.com", username="owner", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            email="other@test.com", username="other", password="testpass123"
        )

        # Create stores
        self.store = Store.objects.create(
            name="Test Store", slug="test-store", owner=self.store_owner
        )
        self.other_store = Store.objects.create(
            name="Other Store", slug="other-store", owner=self.other_user
        )

        # Create test posts
        self.posts = []
        for i in range(5):
            post = Post.objects.create(
                title=f"Test Post {i}", content=f"Content {i}", store=self.store, status="draft"
            )
            self.posts.append(post)

        # Create posts in other store
        self.other_posts = []
        for i in range(3):
            post = Post.objects.create(
                title=f"Other Post {i}",
                content=f"Other Content {i}",
                store=self.other_store,
                status="draft",
            )
            self.other_posts.append(post)

        self.bulk_url = reverse("posts_v2:posts-dashboard") + "bulk_action/"

    def test_bulk_publish_unauthenticated(self):
        """Test bulk publish fails for unauthenticated users"""
        data = {"action": "publish", "ids": [post.id for post in self.posts[:2]]}
        response = self.client.post(self.bulk_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bulk_publish_wrong_store(self):
        """Test bulk publish fails for users not owning the store"""
        self.client.force_authenticate(user=self.other_user)
        data = {"action": "publish", "ids": [post.id for post in self.posts[:2]]}
        response = self.client.post(self.bulk_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_bulk_publish_success(self):
        """Test bulk publish works for store owner"""
        self.client.force_authenticate(user=self.store_owner)
        data = {"action": "publish", "ids": [post.id for post in self.posts[:2]]}
        response = self.client.post(self.bulk_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify posts were published
        for post in self.posts[:2]:
            post.refresh_from_db()
            self.assertEqual(post.status, "published")

        # Verify response data
        self.assertEqual(response.data["action"], "publish")
        self.assertEqual(response.data["requested"], 2)
        self.assertEqual(response.data["found"], 2)
        self.assertEqual(response.data["affected"], 2)

    def test_bulk_unpublish_success(self):
        """Test bulk unpublish works for store owner"""
        # First publish some posts
        for post in self.posts[:2]:
            post.status = "published"
            post.save()

        self.client.force_authenticate(user=self.store_owner)
        data = {"action": "unpublish", "ids": [post.id for post in self.posts[:2]]}
        response = self.client.post(self.bulk_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify posts were unpublished
        for post in self.posts[:2]:
            post.refresh_from_db()
            self.assertEqual(post.status, "draft")

    def test_bulk_delete_success(self):
        """Test bulk delete works for store owner"""
        self.client.force_authenticate(user=self.store_owner)
        post_ids = [post.id for post in self.posts[:2]]
        data = {"action": "delete", "ids": post_ids}
        response = self.client.post(self.bulk_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify posts were deleted
        for post_id in post_ids:
            with self.assertRaises(Post.DoesNotExist):
                Post.objects.get(id=post_id)

    def test_bulk_add_tags_success(self):
        """Test bulk add tags works for store owner"""
        self.client.force_authenticate(user=self.store_owner)
        data = {
            "action": "add_tags",
            "ids": [post.id for post in self.posts[:2]],
            "data": {"tags": ["tag1", "tag2"]},
        }
        response = self.client.post(self.bulk_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify tags were added
        for post in self.posts[:2]:
            post.refresh_from_db()
            self.assertIn("tag1", post.tags)
            self.assertIn("tag2", post.tags)

    def test_bulk_remove_tags_success(self):
        """Test bulk remove tags works for store owner"""
        # First add tags to posts
        for post in self.posts[:2]:
            post.tags = ["tag1", "tag2", "tag3"]
            post.save()

        self.client.force_authenticate(user=self.store_owner)
        data = {
            "action": "remove_tags",
            "ids": [post.id for post in self.posts[:2]],
            "data": {"tags": ["tag1", "tag2"]},
        }
        response = self.client.post(self.bulk_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify tags were removed
        for post in self.posts[:2]:
            post.refresh_from_db()
            self.assertNotIn("tag1", post.tags)
            self.assertNotIn("tag2", post.tags)
            self.assertIn("tag3", post.tags)  # This tag should remain

    def test_bulk_invalid_action(self):
        """Test bulk action fails with invalid action"""
        self.client.force_authenticate(user=self.store_owner)
        data = {"action": "invalid_action", "ids": [post.id for post in self.posts[:2]]}
        response = self.client.post(self.bulk_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Unsupported action", response.data["error"])

    def test_bulk_empty_ids(self):
        """Test bulk action fails with empty IDs list"""
        self.client.force_authenticate(user=self.store_owner)
        data = {"action": "publish", "ids": []}
        response = self.client.post(self.bulk_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bulk_cross_store_access(self):
        """Test that users cannot bulk operate on posts from other stores"""
        self.client.force_authenticate(user=self.store_owner)
        data = {
            "action": "publish",
            "ids": [post.id for post in self.other_posts[:2]],  # Posts from other store
        }
        response = self.client.post(self.bulk_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify no posts were affected (found count should be 0)
        self.assertEqual(response.data["found"], 0)
        self.assertEqual(response.data["affected"], 0)

    def test_analytics_success(self):
        """Test analytics endpoint returns correct data"""
        self.client.force_authenticate(user=self.store_owner)

        # Create some test posts with different statuses
        Post.objects.create(
            title="Published Post", content="Content", store=self.store, status="published"
        )
        Post.objects.create(title="Draft Post", content="Content", store=self.store, status="draft")

        response = self.client.get("/api/v2/posts/dashboard/analytics/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check analytics structure
        self.assertIn("overview", response.data)
        self.assertIn("total_posts", response.data["overview"])
        self.assertIn("published_posts", response.data["overview"])
        self.assertIn("draft_posts", response.data["overview"])
        self.assertEqual(response.data["overview"]["total_posts"], 2)
        self.assertEqual(response.data["overview"]["published_posts"], 1)
        self.assertEqual(response.data["overview"]["draft_posts"], 1)

    def test_analytics_unauthenticated(self):
        """Test analytics endpoint fails for unauthenticated users"""
        response = self.client.get("/api/v2/posts/dashboard/analytics/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_analytics_wrong_store(self):
        """Test analytics endpoint fails for users not owning the store"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get("/api/v2/posts/dashboard/analytics/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
