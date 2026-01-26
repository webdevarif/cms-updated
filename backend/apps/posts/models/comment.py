"""
Comments models - Comment with nested reply support.
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TenantModel

User = get_user_model()


class Comment(TenantModel):
    """Comment model with support for threaded replies"""

    # Core fields
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()

    # Moderation
    is_approved = models.BooleanField(default=False)
    moderation_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )
    is_spam = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    # Helpfulness voting
    helpful_votes = models.PositiveIntegerField(default=0)
    total_votes = models.PositiveIntegerField(default=0)

    # Abuse reporting
    abuse_reports_count = models.PositiveIntegerField(default=0)
    is_hidden = models.BooleanField(default=False)

    # Metadata
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta(TenantModel.Meta):
        db_table = 'posts_comment'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'is_approved', 'created_at']),
            models.Index(fields=['parent', 'is_approved']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['is_approved', 'is_spam']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.user.get_display_name()} on {self.post.title}"

    @property
    def is_reply(self):
        """Check if this comment is a reply to another comment"""
        return self.parent is not None

    @property
    def reply_count(self):
        """Get the number of approved replies to this comment"""
        return self.replies.filter(is_approved=True, is_deleted=False).count()

    @property
    def depth(self):
        """Get the nesting depth of this comment"""
        depth = 0
        parent = self.parent
        while parent:
            depth += 1
            parent = parent.parent
        return depth

    def get_thread(self):
        """Get all comments in this thread (including replies)"""
        thread = [self]
        for reply in self.replies.filter(is_deleted=False).order_by('created_at'):
            thread.extend(reply.get_thread())
        return thread

    def can_reply(self, user):
        """Check if a user can reply to this comment"""
        if not user or not user.is_authenticated:
            return False
        # Additional logic can be added here (e.g., comment locking)
        return True

    def approve(self):
        """Approve this comment"""
        from django.utils import timezone
        self.is_approved = True
        self.approved_at = timezone.now()
        self.save(update_fields=['is_approved', 'approved_at'])

    def reject(self):
        """Reject this comment"""
        self.is_approved = False
        self.save(update_fields=['is_approved'])
