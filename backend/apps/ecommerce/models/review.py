"""
Review models - Product reviews with ratings and moderation.
"""

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class Review(models.Model):
    """Review model for products"""

    # Core fields
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars",
    )
    title = models.CharField(max_length=255)
    content = models.TextField()

    # Moderation
    is_approved = models.BooleanField(default=False)
    moderation_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )
    is_featured = models.BooleanField(default=False)

    # Metadata
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    verified_purchase = models.BooleanField(default=False)

    # Helpfulness voting
    helpful_votes = models.PositiveIntegerField(default=0)
    total_votes = models.PositiveIntegerField(default=0)

    # Abuse reporting
    abuse_reports_count = models.PositiveIntegerField(default=0)
    is_hidden = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "ecommerce_review"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "is_approved", "created_at"]),
            models.Index(fields=["parent", "is_approved"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["rating", "is_approved"]),
            models.Index(fields=["is_approved", "is_featured"]),
            models.Index(fields=["verified_purchase"]),
            models.Index(fields=["created_at"]),
        ]
        unique_together = ("product", "user")  # One review per product per user

    def __str__(self):
        return f"Review by {self.user.get_display_name()} on {self.product.title}"

    @property
    def is_reply(self):
        """Check if this review is a reply to another review"""
        return self.parent is not None

    @property
    def reply_count(self):
        """Get the number of approved replies to this review"""
        return self.replies.filter(is_approved=True).count()

    @property
    def helpful_percentage(self):
        """Calculate helpfulness percentage"""
        if self.total_votes == 0:
            return 0
        return int((self.helpful_votes / self.total_votes) * 100)

    def approve(self):
        """Approve this review"""
        from django.utils import timezone

        self.is_approved = True
        self.approved_at = timezone.now()
        self.save(update_fields=["is_approved", "approved_at"])

    def reject(self):
        """Reject this review"""
        self.is_approved = False
        self.save(update_fields=["is_approved"])

    def add_vote(self, helpful=True):
        """Add a helpfulness vote"""
        self.total_votes += 1
        if helpful:
            self.helpful_votes += 1
        self.save(update_fields=["helpful_votes", "total_votes"])

    def can_reply(self, user):
        """Check if a user can reply to this review"""
        if not user or not user.is_authenticated:
            return False
        # Only store owners/sellers can reply
        return user.is_staff or getattr(user, "store", None) == self.product.store

    def get_thread(self):
        """Get all reviews in this thread (including replies)"""
        thread = [self]
        for reply in self.replies.filter().order_by("created_at"):
            thread.extend(reply.get_thread())
        return thread
