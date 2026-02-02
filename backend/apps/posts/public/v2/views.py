"""Public posts API views."""

from apps.posts.models import Comment, Post
from apps.posts.services.comment_service import CommentService
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import CommentPublicSerializer, PostCreateSerializer, PostSerializer


class PublicPostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "create":
            return PostCreateSerializer
        return PostSerializer


class CommentPublicViewSet(viewsets.GenericViewSet):
    """
    Public read-only access to approved comments for a post.

    All comment creation is handled via authenticated customer endpoints.
    This viewset provides read access to approved, non-spam comments for public display.
    """

    permission_classes = [AllowAny]
    serializer_class = CommentPublicSerializer

    def get_queryset(self):
        """Get approved, non-spam comments for a specific post"""
        post_id = self.kwargs.get("post_pk")
        if post_id:
            return CommentService.get_post_comments(
                post=get_object_or_404(Post, id=post_id), approved_only=True
            ).filter(is_spam=False, is_deleted=False)
        return Comment.objects.none()

    def list(self, request, post_pk=None):
        """List approved comments for a post"""
        post = get_object_or_404(Post, id=post_pk)
        comments = CommentService.get_post_comments(post, approved_only=True)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def vote_helpful(self, request, pk=None):
        """Vote that a comment is helpful"""
        comment = self.get_object()

        if not comment.is_approved:
            return Response({"error": "Cannot vote on unapproved comments"}, status=400)

        # Check if user already voted (simple implementation - in production you'd use a separate Vote model)
        # For now, we'll just increment the vote count
        comment.total_votes += 1
        comment.helpful_votes += 1
        comment.save(update_fields=["total_votes", "helpful_votes"])

        return Response(
            {
                "helpful_votes": comment.helpful_votes,
                "total_votes": comment.total_votes,
                "helpfulness_percentage": comment.helpfulness_percentage,
            }
        )

    @action(detail=True, methods=["post"])
    def report_abuse(self, request, pk=None):
        """Report a comment for abuse"""
        comment = self.get_object()

        # Increment abuse reports count
        comment.abuse_reports_count += 1
        comment.save(update_fields=["abuse_reports_count"])

        # Optionally hide comment if it reaches a threshold
        if comment.abuse_reports_count >= 5:  # Configurable threshold
            comment.is_hidden = True
            comment.save(update_fields=["is_hidden"])

            # Send notification to moderators
            from apps.notifications.services import NotificationService

            try:
                NotificationService.create_notification(
                    user=None,  # System notification to all moderators
                    notification_type="comment_abuse",
                    title="Comment hidden due to abuse reports",
                    message=f'Comment "{comment.content[:50]}..." has been hidden due to {comment.abuse_reports_count} abuse reports',
                    data={
                        "comment_id": comment.id,
                        "post_id": comment.post.id,
                        "abuse_reports_count": comment.abuse_reports_count,
                    },
                    store=comment.store,
                )
            except Exception as e:
                print(f"Failed to send abuse notification: {e}")

        return Response(
            {
                "message": "Abuse report submitted",
                "abuse_reports_count": comment.abuse_reports_count,
                "is_hidden": comment.is_hidden,
            }
        )
