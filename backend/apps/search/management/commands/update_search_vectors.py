"""
Management command to update search vectors for existing records.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.postgres.search import SearchVector, SearchField
from django.db.models import F

from apps.ecommerce.models import Product
from apps.posts.models import Post


class Command(BaseCommand):
    help = 'Update search vectors for all searchable content'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Batch size for updates (default: 100)'
        )
        parser.add_argument(
            '--models',
            type=str,
            help='Comma-separated list of models to update (default: all)'
        )
    
    def handle(self, *args, **options):
        batch_size = options['batch_size']
        models = options.get('models', 'product,post').split(',')
        
        self.stdout.write('Starting search vector updates...')
        
        for model_name in models:
            model_name = model_name.strip().lower()
            
            if model_name == 'product':
                self.update_products(batch_size)
            elif model_name == 'post':
                self.update_posts(batch_size)
            else:
                self.stdout.write(f'Unknown model: {model_name}')
        
        self.stdout.write('Search vector updates completed!')
    
    def update_products(self, batch_size):
        """Update search vectors for all products."""
        self.stdout.write('Updating Product search vectors...')
        
        total = Product.objects.count()
        processed = 0
        
        while processed < total:
            with transaction.atomic():
                # Get batch of products
                products = Product.objects.all()[processed:processed + batch_size]
                
                for product in products:
                    # Create search vector
                    search_vector = SearchVector('title', 'A', 'B', 'C', 'D')
                    
                    # Add tags if available
                    if product.tags:
                        tags_text = ' '.join(product.tags) if product.tags else ''
                        search_vector += SearchVector('E', tags_text)
                    
                    # Add metadata if available
                    if product.metadata:
                        metadata_text = ' '.join(str(v) for v in product.metadata.values() if isinstance(v, str))
                        if metadata_text:
                            search_vector += SearchVector('F', metadata_text)
                    
                    # Update the search vector
                    Product.objects.filter(pk=product.pk).update(search_vector=search_vector)
                
                processed += len(products)
                self.stdout.write(f'  Processed {processed}/{total} products...')
    
    def update_posts(self, batch_size):
        """Update search vectors for all posts."""
        self.stdout.write('Updating Post search vectors...')
        
        total = Post.objects.count()
        processed = 0
        
        while processed < total:
            with transaction.atomic():
                # Get batch of posts
                posts = Post.objects.all()[processed:processed + batch_size]
                
                for post in posts:
                    # Create search vector
                    search_vector = SearchVector('title', 'A', 'B', 'C', 'D')
                    
                    # Add content if available
                    if hasattr(post, 'content'):
                        search_vector += SearchVector('content', 'D', 'E')
                    
                    # Update the search vector
                    Post.objects.filter(pk=post.pk).update(search_vector=search_vector)
                
                processed += len(posts)
                self.stdout.write(f'  Processed {processed}/{total} posts...')
    
    def update_pages(self, batch_size):
        """Update search vectors for all pages."""
        self.stdout.write('Updating Page search vectors...')
        
        # Pages use Post model, so we filter by post type
        total = Post.objects.filter(post_type__slug='page').count()
        processed = 0
        
        while processed < total:
            with transaction.atomic():
                # Get batch of pages
                pages = Post.objects.filter(post_type__slug='page')[processed:processed + batch_size]
                
                for page in pages:
                    # Create search vector
                    search_vector = SearchVector('title', 'A', 'B', 'C', 'D')
                    
                    # Add content if available
                    if hasattr(page, 'content'):
                        search_vector += SearchVector('content', 'D', 'E')
                    
                    # Add meta_description if available
                    if hasattr(page, 'meta_description'):
                        search_vector += SearchVector('meta_description', 'F')
                    
                    # Update the search vector
                    Post.objects.filter(pk=page.pk).update(search_vector=search_vector)
                
                processed += len(pages)
                self.stdout.write(f'  Processed {processed}/{total} pages...')
