"""
Views for post management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from core.permissions import IsStoreOwner
from ..models import Post
from ..services import PostService


class PostViewSet(viewsets.ModelViewSet):
    """API endpoint for managing posts"""
    queryset = Post.objects.select_related('author', 'post_type', 'featured_image')
    permission_classes = [IsAuthenticated, IsStoreOwner]
    
    def get_serializer_class(self):
        from ..serializers import PostSerializer, PostCreateSerializer
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        """Create post with logging"""
        post_type = serializer.validated_data.get('post_type')
        post = PostService.create_post(
            store=self.request.store,
            user=self.request.user,
            post_type=post_type,
            **serializer.validated_data
        )
        serializer.instance = post
    
    @extend_schema(
        summary="Publish post",
        description="Change post status to published",
        tags=["Posts"]
    )
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a post"""
        post = self.get_object()
        published_post = PostService.publish_post(post, request.user)
        return Response({'status': 'published', 'published_at': published_post.published_at})
    
    @extend_schema(
        summary="Unpublish post",
        description="Change post status back to draft",
        tags=["Posts"]
    )
    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        """Unpublish a post"""
        post = self.get_object()
        updated_post = PostService.update_post(
            post, 
            request.user, 
            status='draft', 
            published_at=None
        )
        return Response({'status': 'draft', 'unpublished_at': updated_post.updated_at})
