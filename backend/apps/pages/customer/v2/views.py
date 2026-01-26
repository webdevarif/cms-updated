"""
Customer pages views - authenticated user manages own pages.
Architectural + real implementation for customer pages interface.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from core.permissions import IsStoreUser
from apps.pages.models.pages import Post, PostType
from apps.stores.models import Store
from .serializers import PageCustomerSerializer, PageCustomerListSerializer


class PageCustomerViewSet(viewsets.ModelViewSet):
    """
    Customer pages API - authenticated users manage their own pages.
    Architectural + real implementation for customer pages interface.
    
    Provides:
    - List user's own pages
    - Create new pages
    - Retrieve/update/delete own pages
    - Publish/unpublish actions
    """
    
    permission_classes = [IsAuthenticated, IsStoreUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'content', 'meta_description']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-updated_at']
    filterset_fields = ['status', 'post_type']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return PageCustomerListSerializer
        return PageCustomerSerializer
    
    def get_queryset(self):
        """Filter to user's own pages and page post type."""
        user = self.request.user
        store = getattr(self.request, 'store', None)
        
        queryset = Post.objects.filter(
            author=user,
            store=store
        ).select_related('store', 'featured_image', 'post_type')
        
        # Filter to page post type only
        page_type = PostType.objects.filter(slug='page').first()
        if page_type:
            queryset = queryset.filter(post_type=page_type)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set author and store when creating page."""
        serializer.save(
            author=self.request.user,
            store=getattr(self.request, 'store', None)
        )
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """
        Publish a page.
        
        Args:
            pk: Page ID
            
        Returns:
            Updated page data with published status
        """
        page = self.get_object()
        page.status = 'published'
        page.save()
        
        serializer = self.get_serializer(page)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        """
        Unpublish a page (set to draft).
        
        Args:
            pk: Page ID
            
        Returns:
            Updated page data with draft status
        """
        page = self.get_object()
        page.status = 'draft'
        page.save()
        
        serializer = self.get_serializer(page)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def revisions(self, request, pk=None):
        """
        Get page revision history.
        
        Args:
            pk: Page ID
            
        Returns:
            List of page revisions
        """
        page = self.get_object()
        revisions = page.revisions.all().order_by('-revision_number')
        
        data = []
        for revision in revisions:
            data.append({
                'id': revision.id,
                'revision_number': revision.revision_number,
                'title': revision.title,
                'created_at': revision.created_at,
                'user': revision.user.email if revision.user else None
            })
        
        return Response(data)
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """
        Get page analytics (placeholder for future implementation).
        
        Args:
            pk: Page ID
            
        Returns:
            Basic analytics data
        """
        page = self.get_object()
        
        # Placeholder analytics data
        return Response({
            'page_id': page.id,
            'title': page.title,
            'views': 0,  # To be implemented
            'unique_visitors': 0,  # To be implemented
            'last_viewed': None  # To be implemented
        })
