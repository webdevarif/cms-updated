"""Dashboard posts API views."""

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from apps.posts.models import Post
from apps.posts.v2.serializers import PostSerializer, PostCreateSerializer


class DashboardPostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer
