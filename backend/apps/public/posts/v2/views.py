"""Public posts API views."""

from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from apps.posts.v2.models import Post
from apps.posts.v2.serializers import PostSerializer, PostCreateSerializer
from apps.posts.v2.views.base import StoreScopedViewSet


class PublicPostViewSet(StoreScopedViewSet):
    queryset = Post.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer
