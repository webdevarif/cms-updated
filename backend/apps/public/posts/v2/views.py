"""Public posts API views."""

from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from apps.posts.models import Post
from apps.posts.v2.serializers import PostSerializer, PostCreateSerializer


class PublicPostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer
