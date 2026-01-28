"""Customer posts API views."""

from apps.posts.models import Comment, Post
from apps.posts.services.comment_service import CommentService
from core.permissions import IsStoreUser
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    CommentCustomerSerializer,
    PostCreateSerializer,
    PostSerializer,
    ReplyCreateSerializer,
)


class CustomerPostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated, IsStoreUser]

    def get_serializer_class(self):
        if self.action == "create":
            return PostCreateSerializer
        return PostSerializer


class CommentCustomerViewSet(viewsets.ModelViewSet):
    """Customer comment API - manage own comments and replies"""

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = CommentCustomerSerializer

    def get_queryset(self):
        """Get comments for current user"""
        return CommentService.get_user_comments(
            user=self.request.user, approved_only=False  # Include pending comments
        ).filter(is_deleted=False)

    def perform_create(self, serializer):
        """Create comment is handled in serializer"""
        pass

    def update(self, request, *args, **kwargs):
        """Update own comment"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Check ownership
        if instance.user != request.user:
            return Response(
                {"error": "You can only edit your own comments"}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Soft delete own comment"""
        instance = self.get_object()

        # Check ownership
        if instance.user != request.user:
            return Response(
                {"error": "You can only delete your own comments"}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            CommentService.delete_comment(instance, request.user, soft_delete=True)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def reply(self, request, pk=None):
        """Reply to a specific comment"""
        parent_comment = self.get_object()

        # Check if user can reply
        if not parent_comment.can_reply(request.user):
            return Response(
                {"error": "You cannot reply to this comment"}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = ReplyCreateSerializer(
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
        response_serializer = CommentCustomerSerializer(reply, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
