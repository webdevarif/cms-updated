"""Public posts serializers."""

from rest_framework import serializers
from apps.posts.models import Post, Comment


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content', 'post_type']


class PostSerializer(PostCreateSerializer):
    class Meta(PostCreateSerializer.Meta):
        fields = PostCreateSerializer.Meta.fields + ['id', 'status', 'published_at']


class CommentPublicSerializer(serializers.ModelSerializer):
    """Public comment serializer for read-only list and create operations"""
    user_display_name = serializers.CharField(source='user.get_display_name', read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'user_display_name', 'created_at', 'replies']
        read_only_fields = ['id', 'user_display_name', 'created_at', 'replies']

    def get_replies(self, obj):
        """Get approved replies for this comment"""
        from apps.posts.services.comment_service import CommentService
        replies = CommentService.get_comment_replies(obj)
        return CommentPublicSerializer(replies, many=True, context=self.context).data

    def create(self, validated_data):
        """Create a new comment using CommentService"""
        from apps.posts.services.comment_service import CommentService
        from apps.posts.models import Post

        request = self.context.get('request')
        post_id = self.context.get('post_id')

        if not post_id:
            raise serializers.ValidationError("Post ID is required")

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise serializers.ValidationError("Post not found")

        # Extract additional data from request
        user_ip = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referrer = request.META.get('HTTP_REFERER', '')

        comment = CommentService.create_comment(
            post=post,
            user=request.user,
            content=validated_data['content'],
            user_ip=user_ip,
            user_agent=user_agent,
            referrer=referrer
        )

        return comment

    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
