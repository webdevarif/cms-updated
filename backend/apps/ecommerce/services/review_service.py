"""
Review service for managing product reviews and ratings.
"""
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Avg, Count
from django.utils import timezone
from apps.ecommerce.models import Review, Product, Order, OrderItem
from apps.notifications.services import NotificationService


class ReviewService:
    """Service class for review operations"""

    @staticmethod
    def create_review(product, user, rating, title, content, order_item=None, user_ip=None, user_agent=None, referrer=None):
        """Create a new review"""
        with transaction.atomic():
            # Check if user already reviewed this product
            if Review.objects.filter(product=product, user=user).exists():
                raise ValidationError("You have already reviewed this product")

            # Check if user purchased the product (for verified reviews)
            verified_purchase = ReviewService._check_verified_purchase(user, product, order_item)

            review = Review(
                product=product,
                user=user,
                rating=rating,
                title=title.strip(),
                content=content.strip(),
                verified_purchase=verified_purchase,
                user_ip=user_ip,
                user_agent=user_agent,
                referrer=referrer
            )

            review.full_clean()
            review.save()

            # Update product average rating
            ReviewService._update_product_rating(product)

            # Run spam detection
            spam_result = ReviewService._check_spam(review)
            if spam_result['auto_reject']:
                review.moderation_status = 'rejected'
                review.is_approved = False
                review.save(update_fields=['moderation_status', 'is_approved'])
                # Don't send approval notification, but log spam
                ReviewService._send_spam_notification(review, spam_result)
                return review

            # Send notifications
            ReviewService._send_review_notifications(review)

            # Send real-time WebSocket notification
            ReviewService._send_websocket_review_created(review)

            return review

    @staticmethod
    def update_review(review, user, rating=None, title=None, content=None):
        """Update an existing review"""
        if review.user != user:
            raise ValidationError("You can only edit your own reviews")

        if rating is not None:
            review.rating = rating
        if title is not None:
            review.title = title.strip()
        if content is not None:
            review.content = content.strip()

        review.full_clean()
        review.save()

        # Update product average rating
        ReviewService._update_product_rating(review.product)

        return review

    @staticmethod
    def delete_review(review, user):
        """Delete a review"""
        if review.user != user and not user.is_staff:
            raise ValidationError("You can only delete your own reviews")

        product = review.product
        review.delete()

        # Update product average rating
        ReviewService._update_product_rating(product)

        return True

    @staticmethod
    def moderate_review(review, action, moderator, reason=None):
        """Moderate a review (approve/reject)"""
        if not moderator.is_staff:
            raise ValidationError("Only moderators can moderate reviews")

        if action == 'approve':
            review.moderation_status = 'approved'
            review.is_approved = True
            review.approved_at = timezone.now()
            ReviewService._send_approval_notification(review)
            ReviewService._send_websocket_review_approved(review)
        elif action == 'reject':
            review.moderation_status = 'rejected'
            review.is_approved = False
            ReviewService._send_rejection_notification(review, reason)
            ReviewService._send_websocket_review_rejected(review, reason)
        else:
            raise ValidationError("Invalid moderation action")

        review.save(update_fields=['moderation_status', 'is_approved', 'approved_at'])
        return review

    @staticmethod
    def bulk_moderate_reviews(review_ids, action, moderator, reason=None):
        """Bulk moderate multiple reviews"""
        if not moderator.is_staff:
            raise ValidationError("Only moderators can moderate reviews")

        moderated_reviews = []
        for review_id in review_ids:
            try:
                review = Review.objects.get(id=review_id)
                moderated_review = ReviewService.moderate_review(review, action, moderator, reason)
                moderated_reviews.append(moderated_review)
            except Review.DoesNotExist:
                continue

        return moderated_reviews

    @staticmethod
    def reply_to_review(review, user, content):
        """Reply to a review (seller/admin only)"""
        if not review.can_reply(user):
            raise ValidationError("You cannot reply to this review")

        reply = Review(
            product=review.product,
            user=user,
            parent=review,
            rating=review.rating,  # Same rating as parent
            title=f"Re: {review.title}",
            content=content.strip(),
            is_approved=True,  # Auto-approve seller replies
            verified_purchase=False
        )

        reply.full_clean()
        reply.save()

        # Send reply notification
        ReviewService._send_reply_notification(review, reply)

        return reply

    @staticmethod
    def get_product_reviews(product, approved_only=True, verified_only=False):
        """Get all reviews for a product"""
        queryset = Review.objects.filter(product=product, parent__isnull=True)  # Only top-level reviews

        if approved_only:
            queryset = queryset.filter(is_approved=True)

        if verified_only:
            queryset = queryset.filter(verified_purchase=True)

        return queryset.order_by('-created_at')

    @staticmethod
    def get_product_rating_summary(product):
        """Get rating summary for a product"""
        reviews = Review.objects.filter(
            product=product,
            is_approved=True,
            parent__isnull=True
        )

        if not reviews.exists():
            return {
                'average_rating': 0,
                'total_reviews': 0,
                'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                'verified_reviews': 0
            }

        # Calculate rating distribution
        rating_dist = {}
        verified_count = 0
        for i in range(1, 6):
            count = reviews.filter(rating=i).count()
            rating_dist[i] = count

        verified_count = reviews.filter(verified_purchase=True).count()

        return {
            'average_rating': round(reviews.aggregate(avg=Avg('rating'))['avg'], 1),
            'total_reviews': reviews.count(),
            'rating_distribution': rating_dist,
            'verified_reviews': verified_count
        }

    @staticmethod
    def get_user_reviews(user, approved_only=True):
        """Get all reviews by a specific user"""
        queryset = Review.objects.filter(user=user, parent__isnull=True)

        if approved_only:
            queryset = queryset.filter(is_approved=True)

        return queryset.order_by('-created_at')

    @staticmethod
    def get_pending_reviews(store=None):
        """Get all pending reviews for moderation"""
        queryset = Review.objects.filter(is_approved=False, parent__isnull=True)

        if store:
            queryset = queryset.filter(product__store=store)

        return queryset.order_by('created_at')

    @staticmethod
    def get_review_analytics(store=None, days=30):
        """Get review analytics"""
        from django.utils import timezone

        start_date = timezone.now() - timezone.timedelta(days=days)

        queryset = Review.objects.filter(created_at__gte=start_date)

        if store:
            queryset = queryset.filter(product__store=store)

        return {
            'total_reviews': queryset.count(),
            'approved_reviews': queryset.filter(is_approved=True).count(),
            'pending_reviews': queryset.filter(is_approved=False).count(),
            'verified_reviews': queryset.filter(verified_purchase=True).count(),
            'average_rating': round(queryset.filter(is_approved=True).aggregate(avg=Avg('rating'))['avg'] or 0, 1),
            'helpful_votes_avg': queryset.filter(is_approved=True).aggregate(
                avg_helpfulness=Avg('helpful_votes') / (Avg('total_votes') + 0.001) * 100
            )['avg_helpfulness'] or 0,
            'total_abuse_reports': queryset.aggregate(
                total_reports=Sum('abuse_reports_count')
            )['total_reports'] or 0,
            'hidden_reviews': queryset.filter(is_hidden=True).count(),
            'reviews_by_day': queryset.extra(
                select={'day': 'DATE(created_at)'}
            ).values('day').annotate(count=Count('id')).order_by('day'),
            'rating_distribution': {
                star: queryset.filter(rating=star, is_approved=True).count()
                for star in range(1, 6)
            }
        }

    @staticmethod
    def add_helpful_vote(review, user, helpful=True):
        """Add a helpfulness vote to a review"""
        # In a real implementation, you'd track per-user votes to prevent duplicates
        review.add_vote(helpful)
        return review

    @staticmethod
    def _check_verified_purchase(user, product, order_item=None):
        """Check if user has purchased the product"""
        if order_item:
            # Check specific order item
            return (order_item.order.user == user and
                   order_item.product == product and
                   order_item.order.status in ['completed', 'shipped'])

        # Check if user has any completed orders for this product
        return OrderItem.objects.filter(
            order__user=user,
            product=product,
            order__status__in=['completed', 'shipped']
        ).exists()

    @staticmethod
    def _update_product_rating(product):
        """Update product's average rating"""
        summary = ReviewService.get_product_rating_summary(product)
        # In a real implementation, you might store this in the Product model
        # For now, we'll calculate it on-demand
        pass

    @staticmethod
    def _send_review_notifications(review):
        """Send notifications for new review"""
        try:
            # Notify product store owner
            if review.product.store.owner and review.product.store.owner != review.user:
                NotificationService.create_notification(
                    user=review.product.store.owner,
                    notification_type='product_review',
                    title='New review on your product',
                    message=f'{review.user.get_display_name()} reviewed "{review.product.title}" ({review.rating} stars)',
                    data={
                        'product_id': review.product.id,
                        'review_id': review.id,
                        'rating': review.rating
                    },
                    store=review.product.store
                )

        except Exception as e:
            # Log error but don't fail the review creation
            print(f"Failed to send review notifications: {e}")

    @staticmethod
    def _send_approval_notification(review):
        """Send notification when review is approved"""
        try:
            NotificationService.create_notification(
                user=review.user,
                notification_type='review.approved',  # Use string constant
                title='Your review has been approved',
                message=f'Your review on "{review.product.title}" is now live',
                data={
                    'product_id': review.product.id,
                    'review_id': review.id
                },
                store=review.product.store
            )
        except Exception as e:
            print(f"Failed to send approval notification: {e}")

    @staticmethod
    def _send_rejection_notification(review, reason):
        """Send notification when review is rejected"""
        try:
            NotificationService.create_notification(
                user=review.user,
                notification_type='review.rejected',  # Use string constant
                title='Your review was not approved',
                message=f'Your review on "{review.product.title}" was not approved. Reason: {reason}',
                data={
                    'product_id': review.product.id,
                    'review_id': review.id,
                    'reason': reason
                },
                store=review.product.store
            )
        except Exception as e:
            print(f"Failed to send rejection notification: {e}")

    @staticmethod
    def _check_spam(review):
        """Run spam detection on review"""
        from services.spam_detection_service import SpamDetectionService

        # Combine title and content for spam checking
        full_content = f"{review.title} {review.content}".strip()

        spam_result = SpamDetectionService.check_content(
            content=full_content,
            user=review.user,
            content_type='review',
            store=review.product.store
        )

        # Log spam attempts
        if spam_result['is_spam'] or spam_result['score'] > 0.3:
            SpamDetectionService.log_spam_attempt(
                content=full_content,
                user=review.user,
                content_type='review',
                spam_result=spam_result,
                store=review.product.store
            )

        return spam_result

    @staticmethod
    def _send_spam_notification(review, spam_result):
        """Send notification about spam detection"""
        try:
            NotificationService.create_notification(
                user=review.user,
                notification_type='review_rejected',
                title='Your review was flagged as spam',
                message=f'Your review on "{review.product.title}" was automatically rejected due to spam detection. Reasons: {", ".join(spam_result["reasons"][:2])}',
                data={
                    'product_id': review.product.id,
                    'review_id': review.id,
                    'spam_score': spam_result['score'],
                    'reasons': spam_result['reasons']
                },
                store=review.product.store
            )
        except Exception as e:
            print(f"Failed to send spam notification: {e}")

    @staticmethod
    def _send_websocket_review_created(review):
        """Send WebSocket notification for new review"""
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            from django.utils import timezone

            channel_layer = get_channel_layer()

            # Send to product-specific group
            async_to_sync(channel_layer.group_send)(
                f"product_{review.product.id}_reviews",
                {
                    'type': 'review_created_message',
                    'review': {
                        'id': review.id,
                        'rating': review.rating,
                        'title': review.title,
                        'content': review.content,
                        'user_display_name': review.user.get_display_name(),
                        'verified_purchase': review.verified_purchase,
                        'created_at': review.created_at.isoformat()
                    },
                    'product_id': review.product.id,
                    'timestamp': timezone.now().isoformat()
                }
            )

        except Exception as e:
            # Log error but don't fail the review creation
            print(f"Failed to send WebSocket review notification: {e}")

    @staticmethod
    def _send_websocket_review_approved(review):
        """Send WebSocket notification for approved review"""
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            from django.utils import timezone

            channel_layer = get_channel_layer()

            # Send to product-specific group
            async_to_sync(channel_layer.group_send)(
                f"product_{review.product.id}_reviews",
                {
                    'type': 'review_approved_message',
                    'review': {
                        'id': review.id,
                        'rating': review.rating,
                        'title': review.title,
                        'content': review.content,
                        'user_display_name': review.user.get_display_name(),
                        'verified_purchase': review.verified_purchase,
                        'created_at': review.created_at.isoformat()
                    },
                    'product_id': review.product.id,
                    'timestamp': timezone.now().isoformat()
                }
            )

        except Exception as e:
            print(f"Failed to send WebSocket approval notification: {e}")

    @staticmethod
    def _send_websocket_review_rejected(review, reason=None):
        """Send WebSocket notification for rejected review"""
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            from django.utils import timezone

            channel_layer = get_channel_layer()

            # Send to product-specific group
            async_to_sync(channel_layer.group_send)(
                f"product_{review.product.id}_reviews",
                {
                    'type': 'review_rejected_message',
                    'review': {
                        'id': review.id,
                        'rating': review.rating,
                        'title': review.title,
                        'content': review.content,
                        'user_display_name': review.user.get_display_name(),
                        'verified_purchase': review.verified_purchase,
                        'created_at': review.created_at.isoformat()
                    },
                    'product_id': review.product.id,
                    'reason': reason,
                    'timestamp': timezone.now().isoformat()
                }
            )

        except Exception as e:
            print(f"Failed to send WebSocket rejection notification: {e}")

    @staticmethod
    def _send_reply_notification(review, reply):
        """Send notification when seller replies to review"""
        try:
            NotificationService.create_notification(
                user=review.user,
                notification_type='review_reply',
                title='Seller replied to your review',
                message=f'The seller replied to your review on "{review.product.title}"',
                data={
                    'product_id': review.product.id,
                    'review_id': review.id,
                    'reply_id': reply.id
                },
                store=review.product.store
            )
        except Exception as e:
            print(f"Failed to send reply notification: {e}")
