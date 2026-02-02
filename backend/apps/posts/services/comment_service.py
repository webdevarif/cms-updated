"""
Comment service for managing comments and replies.
"""

from apps.analytics.services.event_service import EventService
from apps.notifications.services import NotificationService
from apps.posts.models import Comment
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone


class CommentService:
    """Service class for comment operations"""

    @staticmethod
    def create_comment(
        post,
        user,
        content,
        parent=None,
        user_ip=None,
        user_agent=None,
        referrer=None,
        auto_approve=False,
    ):
        """
        Create a comment (or reply) with all side effects:
        - Validation and parent checking
        - Spam detection
        - Moderation defaults
        - Notifications
        - Logging

        Args:
            post: The post the comment belongs to
            user: The user creating the comment
            content: Comment content
            parent: Parent comment for replies (optional)
            user_ip: User IP address (optional)
            user_agent: User agent string (optional)
            referrer: Referrer URL (optional)
            auto_approve: Whether to auto-approve the comment (for admin replies)
        """
        with transaction.atomic():
            comment = Comment(
                post=post,
                user=user,
                parent=parent,
                content=content.strip(),
                user_ip=user_ip,
                user_agent=user_agent,
                referrer=referrer,
                store=post.store,
            )

            # Validate parent comment exists and belongs to same post
            if parent:
                if parent.post != post:
                    raise ValidationError("Parent comment must belong to the same post")
                if parent.is_deleted:
                    raise ValidationError("Cannot reply to deleted comment")

            comment.full_clean()
            comment.save()

            # Auto-approve comments from authenticated users if configured
            if user.is_authenticated and post.post_type.supports_comments:
                # Check if auto-approval is enabled for this post type
                # For now, we'll leave comments pending approval unless auto_approve is True
                if auto_approve:
                    comment.moderation_status = "approved"
                    comment.is_approved = True
                    comment.approved_at = timezone.now()

            # Run spam detection
            spam_result = CommentService._check_spam(comment)
            if spam_result["auto_reject"]:
                comment.moderation_status = "rejected"
                comment.is_approved = False
                comment.save(update_fields=["moderation_status", "is_approved"])
                # Don't send approval notification, but log spam
                CommentService._send_spam_notification(comment, spam_result)
                return comment

            # Send notifications
            CommentService._send_comment_notifications(comment)

            # Send real-time WebSocket notification
            CommentService._send_websocket_comment_created(comment)

            # Log comment creation
            EventService.log_event(
                event_type="COMMENT_CREATED",
                event_name=f'Comment created on "{post.title}"',
                properties={
                    "user": user.id if user else None,
                    "store": post.store.id,
                    "entity_type": "Comment",
                    "entity_id": comment.id,
                    "post_id": post.id,
                    "post_title": post.title,
                    "comment_content": content[:100],
                },
                user=user,
                store=post.store,
            )

            return comment

    @staticmethod
    def update_comment(comment, user, content):
        """Update an existing comment"""
        if comment.user != user:
            raise ValidationError("You can only edit your own comments")

        if comment.is_deleted:
            raise ValidationError("Cannot edit deleted comment")

        old_content = comment.content
        comment.content = content.strip()
        comment.full_clean()
        comment.save(update_fields=["content", "updated_at"])

        # Log comment update
        EventService.log_event(
            event_type="COMMENT_UPDATED",
            event_name=f'Comment updated on "{comment.post.title}"',
            properties={
                "user": user.id if user else None,
                "store": comment.post.store.id,
                "entity_type": "Comment",
                "entity_id": comment.id,
                "post_id": comment.post.id,
                "post_title": comment.post.title,
                "old_content": old_content[:100],
                "new_content": comment.content[:100],
            },
            user=user,
            store=comment.post.store,
        )

        return comment

    @staticmethod
    def delete_comment(comment, user, soft_delete=True):
        """Delete a comment (soft or hard delete)"""
        # Check permissions
        if comment.user != user and not user.is_staff:
            raise ValidationError("You can only delete your own comments")

        if soft_delete:
            comment.is_deleted = True
            comment.save(update_fields=["is_deleted", "updated_at"])
        else:
            # Hard delete - remove from database
            comment.delete()

        # Log comment deletion
        EventService.log_event(
            event_type="COMMENT_DELETED",
            event_name=f'Comment {"soft deleted" if soft_delete else "hard deleted"} from "{comment.post.title}"',
            properties={
                "user": user.id if user else None,
                "store": comment.post.store.id,
                "entity_type": "Comment",
                "entity_id": comment.id,
                "post_id": comment.post.id,
                "post_title": comment.post.title,
                "soft_delete": soft_delete,
            },
            user=user,
            store=comment.post.store,
        )

        return True

    @staticmethod
    def moderate_comment(comment, action, moderator, reason=None):
        """Moderate a comment (approve/reject)"""
        if not moderator.is_staff:
            raise ValidationError("Only moderators can moderate comments")

        if action == "approve":
            comment.moderation_status = "approved"
            comment.is_approved = True
            comment.approved_at = timezone.now()
            CommentService._send_approval_notification(comment)
            CommentService._send_websocket_comment_approved(comment)
        elif action == "reject":
            comment.moderation_status = "rejected"
            comment.is_approved = False
            CommentService._send_rejection_notification(comment, reason)
            CommentService._send_websocket_comment_rejected(comment, reason)
        else:
            raise ValidationError("Invalid moderation action")

        comment.save(update_fields=["moderation_status", "is_approved", "approved_at"])

        # Log comment moderation
        EventService.log_event(
            event_type="COMMENT_MODERATED",
            event_name=f'Comment {action}ed on "{comment.post.title}"',
            properties={
                "user": moderator.id if moderator else None,
                "store": comment.post.store.id,
                "entity_type": "Comment",
                "entity_id": comment.id,
                "post_id": comment.post.id,
                "post_title": comment.post.title,
                "moderation_action": action,
                "reason": reason,
            },
            user=moderator,
            store=comment.post.store,
        )

        return comment

    @staticmethod
    def bulk_moderate_comments(comment_ids, action, moderator, reason=None):
        """Bulk moderate multiple comments"""
        if not moderator.is_staff:
            raise ValidationError("Only moderators can moderate comments")

        moderated_comments = []
        for comment_id in comment_ids:
            try:
                comment = Comment.objects.get(id=comment_id)
                moderated_comment = CommentService.moderate_comment(
                    comment, action, moderator, reason
                )
                moderated_comments.append(moderated_comment)
            except Comment.DoesNotExist:
                continue

        return moderated_comments

    @staticmethod
    def mark_as_spam(comment, moderator):
        """Mark comment as spam"""
        if not moderator.is_staff:
            raise ValidationError("Only moderators can mark comments as spam")

        comment.is_spam = True
        comment.is_approved = False
        comment.save(update_fields=["is_spam", "is_approved", "updated_at"])

        return comment

    @staticmethod
    def get_post_comments(post, approved_only=True, include_replies=True):
        """Get all comments for a post"""
        queryset = Comment.objects.filter(post=post, is_deleted=False)

        if approved_only:
            queryset = queryset.filter(is_approved=True)

        if include_replies:
            # Return all comments (parent and replies)
            return queryset.order_by("created_at")
        else:
            # Return only top-level comments
            return queryset.filter(parent__isnull=True).order_by("created_at")

    @staticmethod
    def get_comment_replies(comment, approved_only=True):
        """Get replies to a specific comment"""
        queryset = comment.replies.filter(is_deleted=False)

        if approved_only:
            queryset = queryset.filter(is_approved=True)

        return queryset.order_by("created_at")

    @staticmethod
    def get_pending_comments(store=None):
        """Get all pending comments for moderation"""
        queryset = Comment.objects.filter(is_approved=False, is_deleted=False, is_spam=False)

        if store:
            queryset = queryset.filter(store=store)

        return queryset.order_by("created_at")

    @staticmethod
    def get_user_comments(user, approved_only=True):
        """Get all comments by a specific user"""
        queryset = Comment.objects.filter(user=user, is_deleted=False)

        if approved_only:
            queryset = queryset.filter(is_approved=True)

        return queryset.order_by("-created_at")

    @staticmethod
    def get_comment_analytics(store=None, days=30):
        """Get comment analytics"""
        from django.db.models import Count, Q
        from django.utils import timezone

        start_date = timezone.now() - timezone.timedelta(days=days)

        queryset = Comment.objects.filter(created_at__gte=start_date)

        if store:
            queryset = queryset.filter(store=store)

        return {
            "total_comments": queryset.count(),
            "approved_comments": queryset.filter(is_approved=True).count(),
            "pending_comments": queryset.filter(is_approved=False, is_spam=False).count(),
            "spam_comments": queryset.filter(is_spam=True).count(),
            "deleted_comments": queryset.filter(is_deleted=True).count(),
            "helpful_votes_avg": queryset.filter(is_approved=True).aggregate(
                avg_helpfulness=Avg("helpful_votes") / (Avg("total_votes") + 0.001) * 100
            )["avg_helpfulness"]
            or 0,
            "total_abuse_reports": queryset.aggregate(total_reports=Sum("abuse_reports_count"))[
                "total_reports"
            ]
            or 0,
            "hidden_comments": queryset.filter(is_hidden=True).count(),
            "comments_by_day": queryset.extra(select={"day": "DATE(created_at)"})
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day"),
        }

    @staticmethod
    def _send_comment_notifications(comment):
        """Send notifications for new comment"""
        try:
            # Notify post author
            if comment.post.author and comment.post.author != comment.user:
                NotificationService.create_notification(
                    user=comment.post.author,
                    notification_type="comment",
                    title="New comment on your post",
                    message=f'{comment.user.get_display_name()} commented on "{comment.post.title}"',
                    data={
                        "post_id": comment.post.id,
                        "comment_id": comment.id,
                        "comment_content": comment.content[:100],
                    },
                    store=comment.store,
                )

            # Notify parent comment author (for replies)
            if comment.parent and comment.parent.user != comment.user:
                NotificationService.create_notification(
                    user=comment.parent.user,
                    notification_type="comment_reply",
                    title="Someone replied to your comment",
                    message=f"{comment.user.get_display_name()} replied to your comment",
                    data={
                        "post_id": comment.post.id,
                        "comment_id": comment.id,
                        "parent_comment_id": comment.parent.id,
                    },
                    store=comment.store,
                )

        except Exception as e:
            # Log error but don't fail the comment creation
            print(f"Failed to send comment notifications: {e}")

    @staticmethod
    def _send_approval_notification(comment):
        """Send notification when comment is approved"""
        try:
            NotificationService.create_notification(
                user=comment.user,
                notification_type="comment.approved",  # Use string constant
                title="Your comment has been approved",
                message=f'Your comment on "{comment.post.title}" is now live',
                data={"post_id": comment.post.id, "comment_id": comment.id},
                store=comment.store,
            )
        except Exception as e:
            print(f"Failed to send approval notification: {e}")

    @staticmethod
    def _send_rejection_notification(comment, reason):
        """Send notification when comment is rejected"""
        try:
            NotificationService.create_notification(
                user=comment.user,
                notification_type="comment.rejected",  # Use string constant
                title="Your comment was not approved",
                message=f'Your comment on "{comment.post.title}" was not approved. Reason: {reason}',
                data={
                    "post_id": comment.post.id,
                    "comment_id": comment.id,
                    "reason": reason,
                },
                store=comment.store,
            )
        except Exception as e:
            print(f"Failed to send rejection notification: {e}")

    @staticmethod
    def _check_spam(comment):
        """Run spam detection on comment"""
        from core.services.spam_detection import SpamDetectionService

        spam_result = SpamDetectionService.check_content(
            content=comment.content,
            user=comment.user,
            content_type="comment",
            store=comment.store,
        )

        # Log spam attempts
        if spam_result["is_spam"] or spam_result["score"] > 0.3:
            SpamDetectionService.log_spam_attempt(
                content=comment.content,
                user=comment.user,
                content_type="comment",
                spam_result=spam_result,
                store=comment.store,
            )

        return spam_result

    @staticmethod
    def _send_spam_notification(comment, spam_result):
        """Send notification about spam detection"""
        try:
            NotificationService.create_notification(
                user=comment.user,
                notification_type="comment_rejected",
                title="Your comment was flagged as spam",
                message=f'Your comment on "{comment.post.title}" was automatically rejected due to spam detection. Reasons: {", ".join(spam_result["reasons"][:2])}',
                data={
                    "post_id": comment.post.id,
                    "comment_id": comment.id,
                    "spam_score": spam_result["score"],
                    "reasons": spam_result["reasons"],
                },
                store=comment.store,
            )
        except Exception as e:
            print(f"Failed to send spam notification: {e}")

    @staticmethod
    def _send_websocket_comment_created(comment):
        """Send WebSocket notification for new comment"""
        try:
            import json

            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            from django.utils import timezone

            channel_layer = get_channel_layer()

            # Send to post-specific group
            async_to_sync(channel_layer.group_send)(
                f"post_{comment.post.id}_comments",
                {
                    "type": "comment_created_message",
                    "comment": {
                        "id": comment.id,
                        "content": comment.content,
                        "user_display_name": comment.user.get_display_name(),
                        "created_at": comment.created_at.isoformat(),
                        "is_reply": comment.is_reply,
                    },
                    "post_id": comment.post.id,
                    "timestamp": timezone.now().isoformat(),
                },
            )

        except Exception as e:
            # Log error but don't fail the comment creation
            print(f"Failed to send WebSocket comment notification: {e}")

    @staticmethod
    def _send_websocket_comment_approved(comment):
        """Send WebSocket notification for approved comment"""
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            from django.utils import timezone

            channel_layer = get_channel_layer()

            # Send to post-specific group
            async_to_sync(channel_layer.group_send)(
                f"post_{comment.post.id}_comments",
                {
                    "type": "comment_approved_message",
                    "comment": {
                        "id": comment.id,
                        "content": comment.content,
                        "user_display_name": comment.user.get_display_name(),
                        "created_at": comment.created_at.isoformat(),
                        "is_reply": comment.is_reply,
                    },
                    "post_id": comment.post.id,
                    "timestamp": timezone.now().isoformat(),
                },
            )

        except Exception as e:
            print(f"Failed to send WebSocket approval notification: {e}")

    @staticmethod
    def _send_websocket_comment_rejected(comment, reason=None):
        """Send WebSocket notification for rejected comment"""
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            from django.utils import timezone

            channel_layer = get_channel_layer()

            # Send to post-specific group
            async_to_sync(channel_layer.group_send)(
                f"post_{comment.post.id}_comments",
                {
                    "type": "comment_rejected_message",
                    "comment": {
                        "id": comment.id,
                        "content": comment.content,
                        "user_display_name": comment.user.get_display_name(),
                        "created_at": comment.created_at.isoformat(),
                        "is_reply": comment.is_reply,
                    },
                    "post_id": comment.post.id,
                    "reason": reason,
                    "timestamp": timezone.now().isoformat(),
                },
            )

        except Exception as e:
            print(f"Failed to send WebSocket rejection notification: {e}")
