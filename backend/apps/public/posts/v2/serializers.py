"""Public posts serializers."""

from rest_framework import serializers
from apps.posts.v2.models import Post


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content', 'post_type']


class PostSerializer(PostCreateSerializer):
    class Meta(PostCreateSerializer.Meta):
        fields = PostCreateSerializer.Meta.fields + ['id', 'status', 'published_at']
