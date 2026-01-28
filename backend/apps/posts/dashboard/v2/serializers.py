"""Dashboard posts serializers."""

from apps.posts.models import Comment, Post
from rest_framework import serializers


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["title", "content", "post_type"]


class PostSerializer(PostCreateSerializer):
    class Meta(PostCreateSerializer.Meta):
        fields = PostCreateSerializer.Meta.fields + ["id", "status", "published_at"]


class BulkActionSerializer(serializers.Serializer):
    """Serializer for bulk actions on posts"""

    action = serializers.ChoiceField(
        choices=[
            "publish",
            "unpublish",
            "delete",
            "duplicate",
            "archive",
            "restore",
            "add_tags",
            "remove_tags",
            "status_change",
        ]
    )
    ids = serializers.ListField(
        child=serializers.IntegerField(), help_text="List of post IDs to perform action on"
    )
    data = serializers.DictField(
        required=False,
        help_text="Additional data for actions like tag operations, status changes, etc.",
    )


class CommentDashboardSerializer(serializers.ModelSerializer):
    """Dashboard comment serializer for moderation and analytics"""

    user_display_name = serializers.CharField(source="user.get_display_name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    post_title = serializers.CharField(source="post.title", read_only=True)
    replies = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "content",
            "user_display_name",
            "user_email",
            "post_title",
            "created_at",
            "updated_at",
            "is_approved",
            "is_spam",
            "is_deleted",
            "user_ip",
            "user_agent",
            "referrer",
            "replies",
            "reply_count",
        ]
        read_only_fields = [
            "id",
            "user_display_name",
            "user_email",
            "post_title",
            "created_at",
            "updated_at",
            "user_ip",
            "user_agent",
            "referrer",
            "replies",
            "reply_count",
        ]

    def get_replies(self, obj):
        """Get all replies for this comment (including unapproved for moderation)"""
        from apps.posts.services.comment_service import CommentService

        replies = CommentService.get_comment_replies(obj, approved_only=False)
        return CommentDashboardSerializer(replies, many=True, context=self.context).data

    def get_reply_count(self, obj):
        """Get total reply count"""
        return obj.reply_count


class CommentModerationSerializer(serializers.Serializer):
    """Serializer for comment moderation actions"""

    action = serializers.ChoiceField(
        choices=["approve", "reject", "mark_spam", "delete", "restore"]
    )
    comment_ids = serializers.ListField(
        child=serializers.IntegerField(), help_text="List of comment IDs to moderate"
    )
    reason = serializers.CharField(required=False, help_text="Reason for rejection or other action")


class CommentAnalyticsSerializer(serializers.Serializer):
    """Serializer for comment analytics"""

    days = serializers.IntegerField(
        default=30, min_value=1, max_value=365, help_text="Number of days to analyze"
    )
    approved_only = serializers.BooleanField(
        default=False, help_text="Include only approved comments"
    )


class ReplyAsAdminSerializer(serializers.ModelSerializer):
    """Serializer for admins to reply as admin"""

    class Meta:
        model = Comment
        fields = ["content"]

    def create(self, validated_data):
        """Create admin reply using CommentService"""
        from apps.posts.models import Post
        from apps.posts.services.comment_service import CommentService

        request = self.context.get("request")
        parent_id = self.context.get("parent_id")
        post_id = self.context.get("post_id")

        if not post_id:
            raise serializers.ValidationError("Post ID is required")

        if not parent_id:
            raise serializers.ValidationError("Parent comment ID is required")

        try:
            post = Post.objects.get(id=post_id)
            parent = Comment.objects.get(id=parent_id, post=post)
        except (Post.DoesNotExist, Comment.DoesNotExist):
            raise serializers.ValidationError("Post or parent comment not found")

        # Extract additional data from request
        user_ip = self._get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        referrer = request.META.get("HTTP_REFERER", "")

        # Admin replies are auto-approved
        reply = CommentService.create_comment(
            post=post,
            user=request.user,
            content=validated_data["content"],
            parent=parent,
            user_ip=user_ip,
            user_agent=user_agent,
            referrer=referrer,
        )

        # Auto-approve admin replies
        reply.approve()
        reply.save()

        return reply

    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
