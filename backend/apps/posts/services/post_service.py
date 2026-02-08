"""
Posts services - PostService for post operations with logging.
"""

from apps.analytics.services.event_service import EventService

from django.utils import timezone


class PostService:
    """Service class for post operations with logging"""

    @staticmethod
    def create_post(store, user, post_type, **data):
        """Create a new post with validation and logging"""
        from ..models import Post

        # Create post
        post = Post.objects.create(store=store, post_type=post_type, author=user, **data)

        # Log the creation
        EventService.log_event(
            event_type="POST_CREATED",
            event_name=f'Created {post_type.name} "{post.title}"',
            properties={
                "user": user.id if user else None,
                "store": store.id,
                "entity_type": "Post",
                "entity_id": post.id,
                "post_type": post_type.name,
                "title": post.title,
                "slug": post.slug,
                "status": post.status,
            },
            user=user,
            store=store,
        )
        return post

    @staticmethod
    def update_post(post, user, **data):
        """Update existing post with revision tracking and logging"""
        from ..models import PostRevision

        # Create revision before update
        revision = PostRevision.objects.create(
            post=post,
            user=user,
            title=post.title,
            content=post.content,
            excerpt=post.excerpt,
            custom_fields=post.custom_fields,
            revision_number=post.revisions.count() + 1,
        )

        # Update post
        for field, value in data.items():
            setattr(post, field, value)
        post.save()

        # Log the update
        EventService.log_event(
            event_type="POST_UPDATED",
            event_name=f'Updated {post.post_type.name} "{post.title}"',
            properties={
                "user": user.id if user else None,
                "store": post.store.id,
                "entity_type": "Post",
                "entity_id": post.id,
                "post_type": post.post_type.name,
                "title": post.title,
                "slug": post.slug,
                "status": post.status,
                "fields_updated": list(data.keys()),
            },
            user=user,
            store=post.store,
        )
        return post

    @staticmethod
    def publish_post(post, user):
        """Publish a post"""
        post.status = "published"
        post.published_at = timezone.now()
        post.save()

        EventService.log_event(
            event_type="POST_PUBLISHED",
            event_name=f"Published post: {post.title}",
            properties={
                "user": user.id if user else None,
                "store": post.store.id,
                "entity_type": "Post",
                "entity_id": post.id,
                "post_id": str(post.id),
                "post_type": post.post_type.slug,
            },
            user=user,
            store=post.store,
        )
        return post

    @staticmethod
    def delete_post(post, user):
        """Delete a post"""
        title = post.title
        post_id = post.id
        post.delete()

        EventService.log_event(
            event_type="POST_DELETED",
            event_name=f"Deleted post: {title}",
            properties={
                "user": user.id if user else None,
                "store": post.store.id,
                "entity_type": "Post",
                "entity_id": post_id,
                "post_title": title,
            },
            user=user,
            store=post.store,
        )
