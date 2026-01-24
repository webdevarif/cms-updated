"""
Management command to migrate legacy posts.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.stores.models import Store
from ..v2.models import PostType, Post


class Command(BaseCommand):
    help = 'Migrate legacy posts to v2 structure'

    def handle(self, *args, **options):
        self.stdout.write("Starting post migration...")
        
        # Create default post types for each store
        for store in Store.objects.all():
            # Create or get blog post type
            post_type, created = PostType.objects.get_or_create(
                store=store,
                slug='blog',
                defaults={
                    'name': 'Blog Post',
                    'is_public': True,
                    'supports_comments': True
                }
            )
            
            if created:
                self.stdout.write(f"Created post type 'blog' for {store.name}")
        
        # Migrate legacy posts if they exist
        from ..v1.blogs.models import BlogPost
        migrated = 0
        
        try:
            for legacy_post in BlogPost.objects.all():
                post_type = PostType.objects.get(store=legacy_post.store, slug='blog')
                
                Post.objects.update_or_create(
                    legacy_id=legacy_post.id,
                    store=legacy_post.store,
                    defaults={
                        'title': legacy_post.title,
                        'content': legacy_post.content,
                        'post_type': post_type,
                        'status': 'published' if legacy_post.is_published else 'draft',
                        'created_at': legacy_post.created_at,
                        'updated_at': legacy_post.updated_at,
                        'published_at': legacy_post.published_date
                    }
                )
                migrated += 1
        except ImportError:
            self.stdout.write("No legacy posts found, skipping migration")
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully migrated {migrated} posts')
        )
