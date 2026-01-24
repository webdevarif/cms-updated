"""
Index content management command.
"""
from django.core.management.base import BaseCommand
from apps.stores.models import Store
from apps.public.search.services import SearchService


class Command(BaseCommand):
    help = 'Index content'
    
    def add_arguments(self, parser):
        parser.add_argument('--type', type=str, help='Content type (Post, Product, etc.)')
        parser.add_argument('--store', type=str, help='Store slug')
    
    def handle(self, *args, **options):
        content_type = options.get('type')
        store_slug = options.get('store')
        
        if store_slug:
            try:
                store = Store.objects.get(slug=store_slug)
            except Store.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Store with slug '{store_slug}' not found"))
                return
        else:
            # Use first store
            store = Store.objects.first()
            if not store:
                self.stdout.write(self.style.ERROR("No stores found"))
                return
        
        if content_type:
            self.stdout.write(f"Indexing {content_type} content for store: {store.name}")
            SearchService._index_content_type(store, content_type)
            self.stdout.write(self.style.SUCCESS(f"Successfully indexed {content_type} content"))
        else:
            # Index all content types for the store's search index
            from apps.public.search.models import SearchIndex
            
            index = SearchIndex.objects.filter(store=store, is_active=True).first()
            if not index:
                self.stdout.write(self.style.ERROR(f"No active search index found for store {store.name}"))
                return
            
            self.stdout.write(f"Indexing all content types for store: {store.name}")
            for ct in index.content_types:
                self.stdout.write(f"Indexing {ct}...")
                SearchService._index_content_type(store, ct)
                self.stdout.write(self.style.SUCCESS(f"✓ {ct} indexed"))
