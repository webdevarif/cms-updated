"""
Dashboard pages views - full admin interface for page management.
Architectural + real implementation for dashboard pages interface.
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
    PageDashboardListSerializer,
    PageDashboardSerializer,
    PostTypeSerializer,
    TaxonomySerializer,
    TermSerializer,
)


class PageDashboardViewSet(viewsets.ModelViewSet):
    """
    Dashboard pages API - full admin CRUD on all pages.
    Architectural + real implementation for dashboard pages interface.

    Provides:
    - List all pages in store
    - Create/update/delete pages
    - Bulk actions
    - Publish/unpublish actions
    - Revision management
    """

    permission_classes = [IsAuthenticated, IsStoreOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["title", "content", "meta_description"]
    ordering_fields = ["created_at", "updated_at", "title", "status"]
    ordering = ["-updated_at"]
    filterset_fields = ["status", "post_type", "author"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return PageDashboardListSerializer
        return PageDashboardSerializer

    def get_queryset(self):
        """Filter to store pages and page post type."""
        store = getattr(self.request, "store", None)

        queryset = Post.objects.filter(store=store).select_related(
            "store", "featured_image", "post_type", "author"
        )

        # Filter to page post type only
        page_type = PostType.objects.filter(slug="page").first()
        if page_type:
            queryset = queryset.filter(post_type=page_type)

        return queryset

    def perform_create(self, serializer):
        """Create page using PageService."""
        from apps.pages.services.page_service import PageService

        store = getattr(self.request, "store", None)
        data = serializer.validated_data.copy()

        # Remove fields that will be set by service
        data.pop("store", None)
        data.pop("author", None)

        page = PageService.create_page(store=store, author=self.request.user, data=data)

        # Set the instance on serializer for response
        serializer.instance = page

    @action(detail=False, methods=["post"])
    def bulk_action(self, request):
        """
        Perform bulk actions on pages using PageService.
        """
        from apps.pages.services.page_service import PageService

        from .serializers import BulkActionSerializer

        serializer = BulkActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        action_type = serializer.validated_data["action"]
        page_ids = serializer.validated_data["ids"]
        extra_data = serializer.validated_data.get("data", {})

        try:
            store = getattr(self.request, "store", None)
            result = PageService.bulk_action(
                store=store,
                action=action_type,
                page_ids=page_ids,
                user=self.request.user,
                extra_data=extra_data,
            )

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        """
        Publish a page using PageService.
        """
        from apps.pages.services.page_service import PageService

        page = self.get_object()
        try:
            updated_page = PageService.publish_page(page, user=request.user)
            serializer = self.get_serializer(updated_page)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["post"])
    def unpublish(self, request, pk=None):
        """
        Unpublish a page using PageService.
        """
        from apps.pages.services.page_service import PageService

        page = self.get_object()
        try:
            updated_page = PageService.unpublish_page(page, user=request.user)
            serializer = self.get_serializer(updated_page)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["get"])
    def revisions(self, request, pk=None):
        """Get page revision history."""
        page = self.get_object()
        revisions = page.revisions.all().order_by("-revision_number")

        data = []
        for revision in revisions:
            data.append(
                {
                    "id": revision.id,
                    "revision_number": revision.revision_number,
                    "title": revision.title,
                    "created_at": revision.created_at,
                    "user": revision.user.email if revision.user else None,
                }
            )

        return Response(data)

    @action(detail=True, methods=["post"])
    def restore_revision(self, request, pk=None):
        """Restore a page to a specific revision."""
        page = self.get_object()
        revision_id = request.data.get("revision_id")

        if not revision_id:
            return Response(
                {"error": "revision_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            revision = page.revisions.get(id=revision_id)
            page.title = revision.title
            page.content = revision.content
            page.excerpt = revision.excerpt
            page.custom_fields = revision.custom_fields
            page.save()

            serializer = self.get_serializer(page)
            return Response(serializer.data)

        except page.revisions.model.DoesNotExist:
            return Response({"error": "Revision not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get pages analytics and statistics for the store with time-range filtering"""
        store = getattr(self.request, "store", None)
        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        # Parse time range parameters
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        from datetime import datetime

        date_filter = {}
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                date_filter["created_at__gte"] = start_dt
            except ValueError:
                return Response(
                    {"error": "Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                date_filter["created_at__lte"] = end_dt
            except ValueError:
                return Response(
                    {"error": "Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            # Base queryset with date filtering
            base_queryset = self.get_queryset().filter(**date_filter)

            # Get page counts by status
            total_pages = base_queryset.count()
            published_pages = base_queryset.filter(status="published").count()
            draft_pages = base_queryset.filter(status="draft").count()
            scheduled_pages = base_queryset.filter(status="scheduled").count()

            # Get pages by post type
            from django.db.models import Count

            pages_by_type = {}
            type_counts = (
                base_queryset.values("post_type__name")
                .annotate(count=Count("id"))
                .order_by("-count")
            )
            pages_by_type = {
                item["post_type__name"]: item["count"]
                for item in type_counts
                if item["post_type__name"]
            }

            # Get author distribution
            author_counts = (
                base_queryset.values("author__email", "author__first_name", "author__last_name")
                .annotate(count=Count("id"))
                .order_by("-count")[:10]
            )

            authors = []
            for author_data in author_counts:
                if author_data["author__email"]:
                    authors.append(
                        {
                            "email": author_data["author__email"],
                            "name": f"{author_data['author__first_name'] or ''} {author_data['author__last_name'] or ''}".strip()
                            or "Unknown",
                            "pages_count": author_data["count"],
                        }
                    )

            # Get template usage
            template_counts = (
                base_queryset.exclude(template__isnull=True)
                .values("template__name")
                .annotate(count=Count("id"))
                .order_by("-count")[:10]
            )

            templates = [
                {"name": item["template__name"], "count": item["count"]}
                for item in template_counts
                if item["template__name"]
            ]

            # Get publishing trends (daily pages in the time range)
            if start_date and end_date:
                from django.db.models.functions import TruncDate

                publishing_trends = (
                    base_queryset.filter(status="published")
                    .annotate(date=TruncDate("published_at"))
                    .values("date")
                    .annotate(count=Count("id"))
                    .order_by("date")
                )

                trends = [
                    {"date": str(item["date"]), "count": item["count"]}
                    for item in publishing_trends
                ]
            else:
                trends = []

            # Get recent pages
            recent_pages = PageDashboardListSerializer(
                base_queryset.order_by("-created_at")[:5], many=True
            ).data

            analytics_data = {
                "overview": {
                    "total_pages": total_pages,
                    "published_pages": published_pages,
                    "draft_pages": draft_pages,
                    "scheduled_pages": scheduled_pages,
                    "publish_rate": (
                        (published_pages / total_pages * 100) if total_pages > 0 else 0
                    ),
                },
                "by_type": pages_by_type,
                "authors": authors,
                "templates": templates,
                "publishing_trends": trends,
                "recent_pages": recent_pages,
                "engagement": {
                    # Placeholder for future engagement metrics
                    "avg_views_per_page": 0,  # To be implemented with view tracking
                    "total_views": 0,  # To be implemented with view tracking
                    "avg_time_on_page": 0,  # To be implemented with analytics tracking
                },
                "time_range": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "has_date_filter": bool(start_date or end_date),
                },
            }

            return Response(analytics_data)

        except Exception as e:
            return Response(
                {"error": f"Analytics failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def reports(self, request):
        """Get pages reports."""
        period = request.query_params.get("period", "30d")

        # Placeholder report data
        return Response(
            {
                "period": period,
                "pages_created": 0,  # To be implemented
                "pages_published": 0,  # To be implemented
                "total_views": 0,  # To be implemented
                "popular_pages": [],  # To be implemented
            }
        )


class PostTypeViewSet(viewsets.ModelViewSet):
    """Dashboard post types management."""

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = PostTypeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
    filterset_fields = ["is_public", "is_system", "is_hierarchical"]

    def get_queryset(self):
        """Filter to store post types."""
        store = getattr(self.request, "store", None)
        return PostType.objects.filter(store=store).order_by("name")


class TaxonomyViewSet(viewsets.ModelViewSet):
    """Dashboard taxonomy management."""

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = TaxonomySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
    filterset_fields = ["taxonomy_type"]

    def get_queryset(self):
        """Filter to store taxonomies."""
        store = getattr(self.request, "store", None)
        return Taxonomy.objects.filter(store=store).order_by("name")


class TermViewSet(viewsets.ModelViewSet):
    """Dashboard term management."""

    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = TermSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
    filterset_fields = ["taxonomy", "parent"]

    def get_queryset(self):
        """Filter to store terms."""
        store = getattr(self.request, "store", None)
        return (
            Term.objects.filter(store=store).select_related("taxonomy", "parent").order_by("name")
        )
