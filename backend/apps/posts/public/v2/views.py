"""Public posts API views."""

from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.posts.models import Post, Comment
from apps.posts.services.comment_service import CommentService
from .serializers import PostSerializer, PostCreateSerializer, CommentPublicSerializer


class PublicPostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer


class CommentPublicViewSet(viewsets.GenericViewSet):
    """Public comment API - read-only list and create comments"""
    permission_classes = [AllowAny]
    serializer_class = CommentPublicSerializer

    def get_queryset(self):
        """Get comments for a specific post"""
        post_id = self.kwargs.get('post_pk')
        if post_id:
            return CommentService.get_post_comments(
                post=get_object_or_404(Post, id=post_id),
                approved_only=True
            )
        return Comment.objects.none()

    def list(self, request, post_pk=None):
        """List approved comments for a post"""
        post = get_object_or_404(Post, id=post_pk)
        comments = CommentService.get_post_comments(post, approved_only=True)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def vote_helpful(self, request, pk=None):
        """Vote that a comment is helpful"""
        comment = self.get_object()

        if not comment.is_approved:
            return Response({'error': 'Cannot vote on unapproved comments'}, status=400)

        # Check if user already voted (simple implementation - in production you'd use a separate Vote model)
        # For now, we'll just increment the vote count
        comment.total_votes += 1
        comment.helpful_votes += 1
        comment.save(update_fields=['total_votes', 'helpful_votes'])

        return Response({
            'helpful_votes': comment.helpful_votes,
            'total_votes': comment.total_votes,
            'helpfulness_percentage': comment.helpfulness_percentage
        })

    @action(detail=True, methods=['post'])
    def report_abuse(self, request, pk=None):
        """Report a comment for abuse"""
        comment = self.get_object()

        # Increment abuse reports count
        comment.abuse_reports_count += 1
        comment.save(update_fields=['abuse_reports_count'])

        # Optionally hide comment if it reaches a threshold
        if comment.abuse_reports_count >= 5:  # Configurable threshold
            comment.is_hidden = True
            comment.save(update_fields=['is_hidden'])

            # Send notification to moderators
            from apps.notifications.services import NotificationService
            try:
                NotificationService.create_notification(
                    user=None,  # System notification to all moderators
                    notification_type='comment_abuse',
                    title='Comment hidden due to abuse reports',
                    message=f'Comment "{comment.content[:50]}..." has been hidden due to {comment.abuse_reports_count} abuse reports',
                    data={
                        'comment_id': comment.id,
                        'post_id': comment.post.id,
                        'abuse_reports_count': comment.abuse_reports_count
                    },
                    store=comment.store
                )
            except Exception as e:
                print(f"Failed to send abuse notification: {e}")

        return Response({
            'message': 'Abuse report submitted',
            'abuse_reports_count': comment.abuse_reports_count,
            'is_hidden': comment.is_hidden
        })

    def create(self, request, post_pk=None):
        """Create a new comment on a post"""
        post = get_object_or_404(Post, id=post_pk)

        # Check if post supports comments
        if not post.post_type.supports_comments:
            return Response(
                {'error': 'Comments are not enabled for this post type'},
                status=400
            )

        serializer = self.get_serializer(
            data=request.data,
            context={'request': request, 'post_id': post.id}
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        # Return the created comment
        response_serializer = self.get_serializer(comment)
        return Response(response_serializer.data, status=201)
