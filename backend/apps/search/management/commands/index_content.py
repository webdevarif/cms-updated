"""
Management command to index content according to search rules.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.search.services.infrastructure import SearchService


class Command(BaseCommand):
    help = 'Index specific content type for a store'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--store',
            type=str,
            required=True,
            help='Store slug or ID'
        )
        parser.add_argument(
            '--type',
            type=str,
            required=True,
            help='Content type to index (Page, Post, Product)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Batch size for indexing'
        )
    
    def handle(self, *args, **options):
        store_slug = options['store']
        content_type = options['type']
        batch_size = options['batch_size']
        
        try:
            # Get store
            from apps.stores.models import Store
            try:
                store = Store.objects.get(slug=store_slug)
            except Store.DoesNotExist:
                try:
                    store = Store.objects.get(id=int(store_slug))
                except (Store.DoesNotExist, ValueError):
                    raise CommandError(f'Store "{store_slug}" not found')
            
            self.stdout.write(f'Indexing {content_type} for store: {store.name}')
            
            # Index content based on type
            if content_type == 'Product':
                self._index_products(store, batch_size)
            elif content_type == 'Post':
                self._index_posts(store, batch_size)
            elif content_type == 'Page':
                self._index_pages(store, batch_size)
            else:
                raise CommandError(f'Unknown content type: {content_type}')
            
            self.stdout.write(self.style.SUCCESS(f'✅ {content_type} indexing completed'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
            raise CommandError(f'Indexing failed: {e}')
    
    def _index_products(self, store, batch_size):
        """Index products for store"""
        from apps.ecommerce.models import Product
        
        products = Product.objects.filter(store=store)
        total = products.count()
        indexed = 0
        
        self.stdout.write(f'Indexing {total} products...')
        
        for product in products:
            data = {
                'title': product.title,
                'content': product.description,
                'description': product.seo_description or product.description,
                'url': f'/products/{product.slug}/',
                'created_at': product.created_at.isoformat(),
                'price': str(product.price),
                'status': product.status
            }
            
            success = SearchService.index_document(
                store=store,
                document_type='Product',
                document_id=str(product.id),
                data=data
            )
            
            if success:
                indexed += 1
            
            if indexed % batch_size == 0:
                self.stdout.write(f'  Indexed {indexed}/{total} products...')
        
        self.stdout.write(f'  Total products indexed: {indexed}/{total}')
    
    def _index_posts(self, store, batch_size):
        """Index posts for store"""
        from apps.posts.models import Post
        
        posts = Post.objects.filter(store=store)
        total = posts.count()
        indexed = 0
        
        self.stdout.write(f'Indexing {total} posts...')
        
        for post in posts:
            data = {
                'title': post.title,
                'content': getattr(post, 'content', ''),
                'description': getattr(post, 'excerpt', ''),
                'url': f'/posts/{post.slug}/',
                'created_at': post.created_at.isoformat(),
                'status': getattr(post, 'status', 'published')
            }
            
            success = SearchService.index_document(
                store=store,
                document_type='Post',
                document_id=str(post.id),
                data=data
            )
            
            if success:
                indexed += 1
            
            if indexed % batch_size == 0:
                self.stdout.write(f'  Indexed {indexed}/{total} posts...')
        
        self.stdout.write(f'  Total posts indexed: {indexed}/{total}')
    
    def _index_pages(self, store, batch_size):
        """Index pages for store"""
        from apps.posts.models import Post
        
        # Pages are posts with post_type 'page'
        pages = Post.objects.filter(store=store, post_type__slug='page')
        total = pages.count()
        indexed = 0
        
        self.stdout.write(f'Indexing {total} pages...')
        
        for page in pages:
            data = {
                'title': page.title,
                'content': getattr(page, 'content', ''),
                'description': getattr(page, 'meta_description', ''),
                'url': f'/pages/{page.slug}/',
                'created_at': page.created_at.isoformat(),
                'status': getattr(page, 'status', 'published')
            }
            
            success = SearchService.index_document(
                store=store,
                document_type='Page',
                document_id=str(page.id),
                data=data
            )
            
            if success:
                indexed += 1
            
            if indexed % batch_size == 0:
                self.stdout.write(f'  Indexed {indexed}/{total} pages...')
        
        self.stdout.write(f'  Total pages indexed: {indexed}/{total}')
