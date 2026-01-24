"""
Services for posts app.
"""
from django.utils import timezone
from apps.logs.tasks import log_event_async


class PostService:
    """Service class for post operations with logging"""
    
    @staticmethod
    def create_post(store, user, post_type, **data):
        """Create a new post with validation and logging"""
        from .models import Post
        
        # Create post
        post = Post.objects.create(
            store=store,
            post_type=post_type,
            author=user,
            **data
        )
        
        # Log the creation
        log_event_async.delay({
            'event_type': 'POST_CREATED',
            'message': f'Created {post_type.name} "{post.title}"',
            'store': store,
            'user': user,
            'entity_type': 'Post',
            'entity_id': post.id,
            'metadata': {
                'post_id': str(post.id),
                'post_type': post_type.slug,
                'status': post.status
            }
        })
        return post
    
    @staticmethod
    def update_post(post, user, **data):
        """Update existing post with revision tracking and logging"""
        from .models import PostRevision
        
        # Create revision before update
        revision = PostRevision.objects.create(
            post=post,
            user=user,
            title=post.title,
            content=post.content,
            excerpt=post.excerpt,
            custom_fields=post.custom_fields,
            revision_number=post.revisions.count() + 1
        )
        
        # Update post
        for field, value in data.items():
            setattr(post, field, value)
        post.save()
        
        # Log the update
        log_event_async.delay({
            'event_type': 'POST_UPDATED',
            'message': f'Updated {post.post_type.name} "{post.title}"',
            'store': post.store,
            'user': user,
            'entity_type': 'Post',
            'entity_id': post.id,
            'metadata': {
                'post_id': str(post.id),
                'revision_id': str(revision.id),
                'status': post.status
            }
        })
        return post
    
    @staticmethod
    def publish_post(post, user):
        """Publish a post"""
        post.status = 'published'
        post.published_at = timezone.now()
        post.save()
        
        log_event_async.delay({
            'event_type': 'POST_PUBLISHED',
            'message': f'Published post: {post.title}',
            'store': post.store,
            'user': user,
            'entity_type': 'Post',
            'entity_id': post.id,
            'metadata': {
                'post_id': str(post.id),
                'post_type': post.post_type.slug
            }
        })
        return post
    
    @staticmethod
    def delete_post(post, user):
        """Delete a post"""
        title = post.title
        post_id = post.id
        post.delete()
        
        log_event_async.delay({
            'event_type': 'POST_DELETED',
            'message': f'Deleted post: {title}',
            'entity_type': 'Post',
            'entity_id': post_id,
            'metadata': {
                'post_title': title
            }
        })
