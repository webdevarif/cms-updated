"""Public posts serializers."""

from apps.posts.models import Comment, Post
from rest_framework import serializers


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["title", "content", "post_type"]


class PostSerializer(PostCreateSerializer):
    class Meta(PostCreateSerializer.Meta):
        fields = PostCreateSerializer.Meta.fields + ["id", "status", "published_at"]


class CommentPublicSerializer(serializers.ModelSerializer):
    """
    Public comment serializer for read-only operations.

    Used for displaying approved comments to public users.
    Comment creation is handled by customer endpoints.
    """

    user_display_name = serializers.CharField(source="user.get_display_name", read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "content", "user_display_name", "created_at", "replies"]
        read_only_fields = [
            "id",
            "content",
            "user_display_name",
            "created_at",
            "replies",
        ]

    def get_replies(self, obj):
        """Get approved replies for this comment"""
        from apps.posts.services.comment_service import CommentService

        replies = CommentService.get_comment_replies(obj)
        return CommentPublicSerializer(replies, many=True, context=self.context).data
