"""Customer posts serializers."""

from apps.posts.models import Comment, Post
from rest_framework import serializers

from django.core.exceptions import ValidationError


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["title", "content", "post_type"]


class PostSerializer(PostCreateSerializer):
    class Meta(PostCreateSerializer.Meta):
        fields = PostCreateSerializer.Meta.fields + ["id", "status", "published_at"]


class CommentCustomerSerializer(serializers.ModelSerializer):
    """Customer comment serializer for managing own comments and replies"""

    user_display_name = serializers.CharField(source="user.get_display_name", read_only=True)
    replies = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "content",
            "user_display_name",
            "created_at",
            "updated_at",
            "is_approved",
            "replies",
            "can_edit",
            "can_delete",
        ]
        read_only_fields = [
            "id",
            "user_display_name",
            "created_at",
            "updated_at",
            "is_approved",
            "replies",
            "can_edit",
            "can_delete",
        ]

    def get_replies(self, obj):
        """Get approved replies for this comment"""
        from apps.posts.services.comment_service import CommentService

        replies = CommentService.get_comment_replies(obj)
        return CommentCustomerSerializer(replies, many=True, context=self.context).data

    def get_can_edit(self, obj):
        """Check if current user can edit this comment"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.user == request.user and not obj.is_deleted

    def get_can_delete(self, obj):
        """Check if current user can delete this comment"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.user == request.user and not obj.is_deleted

    def create(self, validated_data):
        """Create a comment using CommentService"""
        from apps.posts.models import Post
        from apps.posts.services.comment_service import CommentService

        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise ValidationError("Authentication required")

        # Get post from context or validated_data
        post_id = self.context.get("post_id")
        if not post_id:
            raise ValidationError("Post ID is required")

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise ValidationError("Post not found")

        # Extract additional data from request
        user_ip = self._get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        referrer = request.META.get("HTTP_REFERER", "")

        comment = CommentService.create_comment(
            post=post,
            user=request.user,
            content=validated_data["content"],
            user_ip=user_ip,
            user_agent=user_agent,
            referrer=referrer,
        )

        return comment

    def update(self, instance, validated_data):
        """Update comment using CommentService"""
        from apps.posts.services.comment_service import CommentService

        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise ValidationError("Authentication required")

        return CommentService.update_comment(
            comment=instance, user=request.user, content=validated_data["content"]
        )

    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class ReplyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating replies to comments"""

    class Meta:
        model = Comment
        fields = ["content"]

    def create(self, validated_data):
        """Create a reply using CommentService"""
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

        reply = CommentService.create_comment(
            post=post,
            user=request.user,
            content=validated_data["content"],
            parent=parent,
            user_ip=user_ip,
            user_agent=user_agent,
            referrer=referrer,
        )

        return reply

    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
