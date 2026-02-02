"""
Public pages views - read-only interface for published pages.
Architectural + real implementation for public pages interface.
"""

from apps.pages.models.pages import Post, PostType, Taxonomy, Term
from apps.stores.models import Store
from core.permissions import IsStoreOwner
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    PagePublicListSerializer,
    PagePublicSerializer,
    PostTypeSerializer,
    TaxonomySerializer,
    TermSerializer,
)


class PagePublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public pages API - read-only access to published pages.
    Architectural + real implementation for public pages interface.

    Provides:
    - List published pages
    - Retrieve page by ID
    - Retrieve page by slug
    - Search and filtering capabilities
    """

    permission_classes = []  # AllowAny
    queryset = Post.objects.filter(status="published").select_related("store", "featured_image")
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["title", "content", "meta_description"]
    ordering_fields = ["created_at", "updated_at", "title"]
    ordering = ["-created_at"]
    filterset_fields = ["post_type", "author"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return PagePublicListSerializer
        return PagePublicSerializer

    @action(detail=False, methods=["get"])
    def by_slug(self, request):
        """Get page by slug using PageService for caching."""
        from apps.pages.services.page_service import PageService

        slug = request.query_params.get("slug")
        if not slug:
            return Response(
                {"error": "slug parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        store = getattr(request, "store", None)
        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        # Use PageService for caching benefits
        page_data = PageService.get_page_by_slug(store, slug)
        if page_data:
            return Response(page_data)
        else:
            return Response({"error": "Page not found"}, status=status.HTTP_404_NOT_FOUND)
