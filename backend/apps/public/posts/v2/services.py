"""Public posts services."""

from apps.posts.services import PostService


class PublicPostService(PostService):
    """Public-facing post service with additional safety checks"""
    
    @staticmethod
    def get_published_posts(store, limit=10):
        """Get published posts for public viewing"""
        from apps.posts.models import Post
        
        return Post.objects.filter(
            store=store,
            status='published'
        ).order_by('-published_at')[:limit]
    
    @staticmethod
    def get_post_by_slug(store, slug):
        """Get published post by slug"""
        from apps.posts.models import Post
        
        try:
            return Post.objects.get(
                store=store,
                slug=slug,
                status='published'
            )
        except Post.DoesNotExist:
            return None
