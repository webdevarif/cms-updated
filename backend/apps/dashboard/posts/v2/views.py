"""Dashboard posts API views."""

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from apps.posts.v2.models import Post
from apps.posts.v2.serializers import PostSerializer, PostCreateSerializer
from apps.posts.v2.views.base import StoreScopedViewSet


class DashboardPostViewSet(StoreScopedViewSet):
    queryset = Post.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer
