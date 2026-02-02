"""Dashboard posts API views."""

from apps.posts.models import Post
from apps.posts.models.comment import Comment
from core.permissions import IsStoreAdmin
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    BulkActionSerializer,
    CommentDashboardSerializer,
    PostCreateSerializer,
    PostSerializer,
)


@extend_schema(
    tags=["Content Management"],
    summary="Dashboard Posts Management",
    description="Full CRUD operations for posts in the dashboard. Provides comprehensive post management with bulk operations, analytics, and advanced filtering.",
    parameters=[
        OpenApiParameter(
            name="store",
            description="Store ID to filter posts by",
            required=False,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
    ],
)
class DashboardPostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated, IsStoreAdmin]

    def get_queryset(self):
        """Filter posts by store"""
        return Post.objects.filter(store=self.request.store)

    def get_serializer_class(self):
        if self.action == "create":
            return PostCreateSerializer
        return PostSerializer

    def perform_create(self, serializer):
        """Set store when creating post"""
        serializer.save(store=self.request.store)

    @extend_schema(
        summary="Create new post",
        description="Create a new post in the dashboard with automatic store assignment",
        request=PostCreateSerializer,
        responses={
            201: PostSerializer,
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Permission denied"),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="List posts",
        description="Retrieve paginated list of posts for the authenticated store",
        parameters=[
            OpenApiParameter(name="page", description="Page number", type=int),
            OpenApiParameter(name="page_size", description="Items per page", type=int),
            OpenApiParameter(name="search", description="Search in title and content", type=str),
            OpenApiParameter(name="status", description="Filter by status", type=str),
        ],
        responses={
            200: PostSerializer(many=True),
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve post",
        description="Get detailed information about a specific post",
        responses={
            200: PostSerializer,
            404: OpenApiResponse(description="Post not found"),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update post",
        description="Update an existing post with new data",
        request=PostSerializer,
        responses={
            200: PostSerializer,
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Post not found"),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partial update post",
        description="Partially update a post with provided fields",
        request=PostSerializer,
        responses={
            200: PostSerializer,
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Post not found"),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete post",
        description="Delete a post permanently",
        responses={
            204: OpenApiResponse(description="Post deleted successfully"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Post not found"),
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary="Bulk actions on posts",
        description="Perform bulk operations on multiple posts including publish/unpublish, duplicate, archive, restore, and status changes",
        request=BulkActionSerializer,
        responses={
            200: OpenApiResponse(
                description="Bulk operation completed successfully",
                examples=[
                    {
                        "message": "Successfully published 5 posts",
                        "action": "publish",
                        "requested": 5,
                        "found": 5,
                        "affected": 5,
                        "results": [
                            {"id": 123, "status": "success"},
                            {"id": 124, "status": "success"},
                        ],
                    }
                ],
            ),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Permission denied"),
        },
    )
    @action(detail=False, methods=["post"])
    def bulk_action(self, request):
        """Perform bulk actions on posts (publish, unpublish, delete, tag operations)"""
        serializer = BulkActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        action_type = serializer.validated_data["action"]
        post_ids = serializer.validated_data["ids"]
        extra_data = serializer.validated_data.get("data", {})

        # Filter posts by store and IDs
        queryset = self.get_queryset().filter(id__in=post_ids)
        total_requested = len(post_ids)
        total_found = queryset.count()

        try:
            with transaction.atomic():
                if action_type == "publish":
                    updated = queryset.update(status="published")
                    message = f"Successfully published {updated} posts"

                elif action_type == "unpublish":
                    updated = queryset.update(status="draft")
                    message = f"Successfully unpublished {updated} posts"

                elif action_type == "delete":
                    deleted = queryset.delete()[0]  # delete() returns (count, details)
                    message = f"Successfully deleted {deleted} posts"

                elif action_type == "add_tags":
                    tags_to_add = extra_data.get("tags", [])
                    if not tags_to_add:
                        return Response(
                            {"error": "No tags specified for add_tags action"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    updated_count = 0
                    for post in queryset:
                        current_tags = set(post.tags or [])
                        current_tags.update(tags_to_add)
                        post.tags = list(current_tags)
                        post.save(update_fields=["tags"])
                        updated_count += 1

                    message = f"Successfully added tags {tags_to_add} to {updated_count} posts"

                elif action_type == "remove_tags":
                    tags_to_remove = extra_data.get("tags", [])
                    if not tags_to_remove:
                        return Response(
                            {"error": "No tags specified for remove_tags action"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    results = []
                    for post in queryset:
                        try:
                            current_tags = set(post.tags or [])
                            current_tags.difference_update(tags_to_remove)
                            post.tags = list(current_tags)
                            post.save(update_fields=["tags"])
                            results.append({"id": post.id, "status": "success"})
                        except Exception as e:
                            results.append({"id": post.id, "status": "error", "error": str(e)})

                    success_count = sum(1 for r in results if r["status"] == "success")
                    message = (
                        f"Successfully removed tags {tags_to_remove} from {success_count} posts"
                    )

                elif action_type == "duplicate":
                    results = []
                    for post in queryset:
                        try:
                            # Create a duplicate of the post
                            duplicate_data = {
                                "title": f"{post.title} (Copy)",
                                "content": post.content,
                                "excerpt": post.excerpt,
                                "status": "draft",  # Duplicates start as drafts
                                "post_type": post.post_type,
                                "author": post.author,
                                "store": post.store,
                                "featured_image": post.featured_image,
                                "tags": post.tags,
                                "custom_fields": post.custom_fields,
                                "meta_title": post.meta_title,
                                "meta_description": post.meta_description,
                                "meta_keywords": post.meta_keywords,
                            }
                            duplicate_post = Post.objects.create(**duplicate_data)
                            results.append(
                                {
                                    "id": post.id,
                                    "status": "success",
                                    "duplicate_id": duplicate_post.id,
                                }
                            )
                        except Exception as e:
                            results.append({"id": post.id, "status": "error", "error": str(e)})

                    success_count = sum(1 for r in results if r["status"] == "success")
                    message = f"Successfully duplicated {success_count} posts"

                elif action_type == "archive":
                    results = []
                    for post in queryset:
                        try:
                            # Archive posts (could set a custom status or metadata)
                            if not hasattr(post, "custom_fields"):
                                post.custom_fields = {}
                            post.custom_fields["archived"] = True
                            post.custom_fields["archived_at"] = str(timezone.now())
                            post.save(update_fields=["custom_fields"])
                            results.append({"id": post.id, "status": "success"})
                        except Exception as e:
                            results.append({"id": post.id, "status": "error", "error": str(e)})

                    success_count = sum(1 for r in results if r["status"] == "success")
                    message = f"Successfully archived {success_count} posts"

                elif action_type == "restore":
                    results = []
                    for post in queryset:
                        try:
                            # Restore archived posts
                            if hasattr(post, "custom_fields") and post.custom_fields:
                                post.custom_fields.pop("archived", None)
                                post.custom_fields.pop("archived_at", None)
                                post.save(update_fields=["custom_fields"])
                            results.append({"id": post.id, "status": "success"})
                        except Exception as e:
                            results.append({"id": post.id, "status": "error", "error": str(e)})

                    success_count = sum(1 for r in results if r["status"] == "success")
                    message = f"Successfully restored {success_count} posts"

                elif action_type == "status_change":
                    new_status = extra_data.get("status")
                    if not new_status:
                        return Response(
                            {"error": "No status specified for status_change action"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    valid_statuses = ["draft", "published", "scheduled", "archived"]
                    if new_status not in valid_statuses:
                        return Response(
                            {
                                "error": f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    results = []
                    for post in queryset:
                        try:
                            post.status = new_status
                            if new_status == "published" and not post.published_at:
                                post.published_at = timezone.now()
                            post.save(update_fields=["status", "published_at"])
                            results.append(
                                {
                                    "id": post.id,
                                    "status": "success",
                                    "new_status": new_status,
                                }
                            )
                        except Exception as e:
                            results.append({"id": post.id, "status": "error", "error": str(e)})

                    success_count = sum(1 for r in results if r["status"] == "success")
                    message = (
                        f"Successfully changed status to {new_status} for {success_count} posts"
                    )

                else:
                    return Response(
                        {"error": f"Unsupported action: {action_type}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Log the bulk operation
                from apps.analytics.services.event_service import EventService

                EventService.log_event(
                    event_type="CONTENT_BULK_UPDATE",
                    event_name=f"Bulk {action_type} operation on posts",
                    properties={
                        "user": request.user.id if request.user else None,
                        "store": request.store.id,
                        "action_type": action_type,
                        "count": len(post_ids),
                        "post_ids": post_ids,
                    },
                    user=request.user,
                    store=request.store,
                )

                return Response(
                    {
                        "message": message,
                        "action": action_type,
                        "requested": total_requested,
                        "found": total_found,
                        "affected": sum(1 for r in results if r["status"] == "success"),
                        "results": results,  # Detailed per-ID results
                    }
                )

        except Exception as e:
            return Response(
                {"error": f"Bulk operation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Post analytics and statistics",
        description="Get comprehensive analytics for posts including status distribution, author stats, publishing trends, and time-range filtering",
        parameters=[
            OpenApiParameter(
                name="start_date",
                description="Start date for analytics filtering (ISO format)",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="end_date",
                description="End date for analytics filtering (ISO format)",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Post analytics data",
                examples=[
                    {
                        "overview": {
                            "total_posts": 150,
                            "published_posts": 120,
                            "draft_posts": 25,
                            "scheduled_posts": 5,
                            "publish_rate": 80.0,
                        },
                        "authors": [{"email": "author@example.com", "posts_count": 45}],
                        "publishing_trends": [{"date": "2024-01-15", "count": 8}],
                    }
                ],
            ),
            400: OpenApiResponse(description="Invalid date format"),
            403: OpenApiResponse(description="Permission denied"),
        },
    )
    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get posts analytics and statistics for the store with time-range filtering"""
        store = getattr(self.request, "store", None)
        if not store:
            return Response({"error": "Store context required"}, status=status.HTTP_400_BAD_REQUEST)

        # Parse time range parameters
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        from datetime import datetime

        from django.utils import timezone

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
            base_queryset = Post.objects.filter(store=store, **date_filter)

            # Get post counts by status
            total_posts = base_queryset.count()
            published_posts = base_queryset.filter(status="published").count()
            draft_posts = base_queryset.filter(status="draft").count()
            scheduled_posts = base_queryset.filter(status="scheduled").count()

            # Get posts by type (if applicable)
            posts_by_type = {}
            if hasattr(Post, "post_type"):
                from django.db.models import Count

                type_counts = (
                    base_queryset.values("post_type__name")
                    .annotate(count=Count("id"))
                    .order_by("-count")
                )
                posts_by_type = {
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
                            "posts_count": author_data["count"],
                        }
                    )

            # Get popular tags (if tags field exists)
            popular_tags = {}
            if hasattr(Post, "tags"):
                from django.db.models import Count

                tag_counts = (
                    base_queryset.exclude(tags__isnull=True)
                    .exclude(tags__exact="")
                    .values_list("tags", flat=True)
                )
                tag_dict = {}
                for tag_list in tag_counts:
                    if tag_list:
                        for tag in tag_list:
                            tag_dict[tag] = tag_dict.get(tag, 0) + 1
                popular_tags = dict(sorted(tag_dict.items(), key=lambda x: x[1], reverse=True)[:10])

            # Get publishing trends (daily posts in the time range)
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

            analytics_data = {
                "overview": {
                    "total_posts": total_posts,
                    "published_posts": published_posts,
                    "draft_posts": draft_posts,
                    "scheduled_posts": scheduled_posts,
                    "publish_rate": (
                        (published_posts / total_posts * 100) if total_posts > 0 else 0
                    ),
                },
                "by_type": posts_by_type,
                "authors": authors,
                "popular_tags": popular_tags,
                "publishing_trends": trends,
                "engagement": {
                    # Placeholder for future engagement metrics
                    "avg_views_per_post": 0,  # To be implemented with view tracking
                    "total_views": 0,  # To be implemented with view tracking
                    "avg_engagement_rate": 0,  # To be implemented with engagement tracking
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


class CommentDashboardViewSet(viewsets.ModelViewSet):
    """
    Admin-only comment moderation and management.

    Handles bulk operations, approval, rejection, spam marking, and analytics.
    All moderation actions use CommentService methods for consistent behavior.
    """

    permission_classes = [IsAuthenticated, IsStoreAdmin]
    serializer_class = CommentDashboardSerializer

    def get_queryset(self):
        """Get all comments for moderation"""
        store_id = self.request.query_params.get("store")
        if store_id:
            return Comment.objects.filter(store_id=store_id)
        return Comment.objects.all()

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "moderate":
            return CommentModerationSerializer
        elif self.action == "analytics":
            return CommentAnalyticsSerializer
        elif self.action == "reply_as_admin":
            return ReplyAsAdminSerializer
        return CommentDashboardSerializer

    def list(self, request, *args, **kwargs):
        """List comments with filtering options"""
        queryset = self.get_queryset()

        # Filter by approval status
        approved = request.query_params.get("approved")
        if approved is not None:
            queryset = queryset.filter(is_approved=approved.lower() == "true")

        # Filter by spam status
        spam = request.query_params.get("spam")
        if spam is not None:
            queryset = queryset.filter(is_spam=spam.lower() == "true")

        # Filter by post
        post_id = request.query_params.get("post_id")
        if post_id:
            queryset = queryset.filter(post_id=post_id)

        # Filter by date range
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        # Order by creation date (newest first)
        queryset = queryset.order_by("-created_at")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Update comment (approve/reject/mark spam)"""
        instance = self.get_object()
        action = request.data.get("action")

        try:
            from apps.posts.services.comment_service import CommentService

            if action == "approve":
                CommentService.approve_comment(instance, request.user)
            elif action == "reject":
                reason = request.data.get("reason", "Rejected by moderator")
                CommentService.reject_comment(instance, request.user, reason)
            elif action == "mark_spam":
                CommentService.mark_as_spam(instance, request.user)
            else:
                return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Hard delete comment (admin only)"""
        instance = self.get_object()

        try:
            from apps.posts.services.comment_service import CommentService

            CommentService.delete_comment(instance, request.user, soft_delete=False)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def moderate(self, request):
        """
        Bulk moderation actions (admin-only).

        Handles bulk approve, reject, mark_spam, and delete operations
        on multiple comments using CommentService for consistency.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data["action"]
        comment_ids = serializer.validated_data["comment_ids"]
        reason = serializer.validated_data.get("reason")

        try:
            from apps.posts.services.comment_service import CommentService

            moderated_count = 0
            for comment_id in comment_ids:
                try:
                    comment = Comment.objects.get(id=comment_id)

                    if action == "approve":
                        CommentService.approve_comment(comment, request.user)
                    elif action == "reject":
                        CommentService.reject_comment(comment, request.user, reason)
                    elif action == "mark_spam":
                        CommentService.mark_as_spam(comment, request.user)
                    elif action == "delete":
                        CommentService.delete_comment(comment, request.user, soft_delete=True)
                    elif action == "restore":
                        # Restore soft-deleted comment
                        comment.is_deleted = False
                        comment.save(update_fields=["is_deleted"])

                    moderated_count += 1

                except Comment.DoesNotExist:
                    continue

            return Response(
                {
                    "message": f"Successfully moderated {moderated_count} comments",
                    "action": action,
                    "moderated_count": moderated_count,
                }
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get comprehensive comment analytics"""
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        days = serializer.validated_data.get("days", 30)
        approved_only = serializer.validated_data.get("approved_only", False)

        # Parse date filters
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        try:
            from apps.posts.services.comment_service import CommentService
            from django.db.models import Count, Q
            from django.utils import timezone

            store = getattr(request.user, "store", None)

            # Base analytics from service
            analytics = CommentService.get_comment_analytics(store=store, days=days)

            # Enhanced analytics with date filtering and additional metrics
            start_dt = None
            end_dt = None

            if start_date:
                start_dt = timezone.datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            if end_date:
                end_dt = timezone.datetime.fromisoformat(end_date.replace("Z", "+00:00"))

            # If custom date range provided, override days
            if start_dt or end_dt:
                if not start_dt:
                    start_dt = timezone.now() - timezone.timedelta(days=30)
                if not end_dt:
                    end_dt = timezone.now()

                # Recalculate analytics for custom date range
                queryset = Comment.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt)
                if store:
                    queryset = queryset.filter(store=store)

                analytics = {
                    "total_comments": queryset.count(),
                    "approved_comments": queryset.filter(is_approved=True).count(),
                    "pending_comments": queryset.filter(moderation_status="pending").count(),
                    "rejected_comments": queryset.filter(moderation_status="rejected").count(),
                    "spam_comments": queryset.filter(is_spam=True).count(),
                    "deleted_comments": queryset.filter(is_deleted=True).count(),
                    "comments_by_day": queryset.extra(select={"day": "DATE(created_at)"})
                    .values("day")
                    .annotate(count=Count("id"))
                    .order_by("day"),
                }

            # Add top commenters
            top_commenters = (
                Comment.objects.filter(
                    store=store if store else Q(),
                    is_approved=True,
                    created_at__gte=timezone.now() - timezone.timedelta(days=days),
                )
                .values("user__username", "user__get_display_name")
                .annotate(comment_count=Count("id"))
                .order_by("-comment_count")[:10]
            )

            # Add moderation statistics
            moderation_stats = {
                "pending_review": Comment.objects.filter(
                    store=store if store else Q(),
                    moderation_status="pending",
                    created_at__gte=timezone.now() - timezone.timedelta(days=days),
                ).count(),
                "recently_approved": Comment.objects.filter(
                    store=store if store else Q(),
                    moderation_status="approved",
                    approved_at__gte=timezone.now() - timezone.timedelta(days=days),
                ).count(),
                "recently_rejected": Comment.objects.filter(
                    store=store if store else Q(),
                    moderation_status="rejected",
                    updated_at__gte=timezone.now() - timezone.timedelta(days=days),
                ).count(),
            }

            # Filter approved-only if requested
            if approved_only:
                analytics = {
                    k: v
                    for k, v in analytics.items()
                    if "approved" in k.lower() or "total" in k.lower()
                }

            # Combine all analytics
            full_analytics = {
                **analytics,
                "top_commenters": list(top_commenters),
                "moderation_stats": moderation_stats,
                "time_range": {
                    "start_date": (
                        start_dt or (timezone.now() - timezone.timedelta(days=days))
                    ).isoformat(),
                    "end_date": (end_dt or timezone.now()).isoformat(),
                    "days": days,
                    "has_custom_range": bool(start_date or end_date),
                },
            }

            return Response(full_analytics)

        except Exception as e:
            return Response(
                {"error": f"Analytics failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def reply_as_admin(self, request, pk=None):
        """Reply to a comment as admin (auto-approved)"""
        parent_comment = self.get_object()

        serializer = self.get_serializer(
            data=request.data,
            context={
                "request": request,
                "parent_id": parent_comment.id,
                "post_id": parent_comment.post.id,
            },
        )
        serializer.is_valid(raise_exception=True)
        reply = serializer.save()

        # Return the created reply
        response_serializer = CommentDashboardSerializer(reply, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def pending(self, request):
        """Get all pending comments for moderation"""
        queryset = Comment.objects.filter(
            moderation_status="pending", is_deleted=False
        ).select_related("user", "post")

        # Filter by store if specified
        store_id = request.query_params.get("store")
        if store_id:
            queryset = queryset.filter(store_id=store_id)

        # Order by creation date (oldest first for moderation priority)
        queryset = queryset.order_by("created_at")

        # Add pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a pending comment"""
        comment = self.get_object()

        try:
            from apps.posts.services.comment_service import CommentService

            CommentService.moderate_comment(comment, "approve", request.user)

            # Get updated comment with moderation history
            serializer = self.get_serializer(comment)
            response_data = serializer.data
            response_data["moderation_history"] = [
                {
                    "action": "approved",
                    "moderator": request.user.get_display_name(),
                    "timestamp": (comment.approved_at.isoformat() if comment.approved_at else None),
                    "reason": None,
                }
            ]

            return Response(response_data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject a comment with optional reason"""
        comment = self.get_object()
        reason = request.data.get("reason", "Rejected by moderator")

        try:
            from apps.posts.services.comment_service import CommentService

            CommentService.moderate_comment(comment, "reject", request.user, reason)

            # Get updated comment with moderation history
            serializer = self.get_serializer(comment)
            response_data = serializer.data
            response_data["moderation_history"] = [
                {
                    "action": "rejected",
                    "moderator": request.user.get_display_name(),
                    "timestamp": timezone.now().isoformat(),
                    "reason": reason,
                }
            ]

            return Response(response_data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def moderation_queue(self, request):
        """Get pending comments for moderation"""
        queryset = Comment.objects.filter(moderation_status="pending", is_deleted=False)

        # Filter by store if specified
        store_id = request.query_params.get("store")
        if store_id:
            queryset = queryset.filter(store_id=store_id)

        # Order by creation date (oldest first for moderation priority)
        queryset = queryset.order_by("created_at")

        # Add pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a pending comment"""
        comment = self.get_object()

        try:
            from apps.posts.services.comment_service import CommentService

            CommentService.moderate_comment(comment, "approve", request.user)
            serializer = self.get_serializer(comment)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject a comment with optional reason"""
        comment = self.get_object()
        reason = request.data.get("reason", "Rejected by moderator")

        try:
            from apps.posts.services.comment_service import CommentService

            CommentService.moderate_comment(comment, "reject", request.user, reason)
            serializer = self.get_serializer(comment)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def bulk_moderate(self, request):
        """Bulk moderate multiple comments"""
        serializer = CommentModerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data["action"]
        comment_ids = serializer.validated_data["comment_ids"]
        reason = serializer.validated_data.get("reason")

        try:
            from apps.posts.services.comment_service import CommentService
            from django.utils import timezone

            moderated_comments = []
            moderation_history = []

            for comment_id in comment_ids:
                try:
                    comment = Comment.objects.get(id=comment_id)
                    CommentService.moderate_comment(comment, action, request.user, reason)

                    moderated_comments.append(comment)
                    moderation_history.append(
                        {
                            "comment_id": comment.id,
                            "action": action,
                            "moderator": request.user.get_display_name(),
                            "timestamp": timezone.now().isoformat(),
                            "reason": reason,
                        }
                    )

                except Comment.DoesNotExist:
                    continue
                except ValidationError:
                    continue

            return Response(
                {
                    "message": f"Successfully moderated {len(moderated_comments)} comments",
                    "action": action,
                    "moderated_count": len(moderated_comments),
                    "moderation_history": moderation_history,
                }
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def bulk_mark_spam(self, request):
        """Bulk mark multiple comments as spam"""
        serializer = CommentModerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment_ids = serializer.validated_data["comment_ids"]
        reason = serializer.validated_data.get("reason", "Marked as spam by moderator")

        try:
            from apps.posts.services.comment_service import CommentService
            from django.utils import timezone

            marked_comments = []
            moderation_history = []

            for comment_id in comment_ids:
                try:
                    comment = Comment.objects.get(id=comment_id)
                    CommentService.mark_as_spam(comment, request.user)

                    marked_comments.append(comment)
                    moderation_history.append(
                        {
                            "comment_id": comment.id,
                            "action": "marked_spam",
                            "moderator": request.user.get_display_name(),
                            "timestamp": timezone.now().isoformat(),
                            "reason": reason,
                        }
                    )

                except Comment.DoesNotExist:
                    continue
                except ValidationError:
                    continue

            return Response(
                {
                    "message": f"Successfully marked {len(marked_comments)} comments as spam",
                    "marked_count": len(marked_comments),
                    "moderation_history": moderation_history,
                }
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
