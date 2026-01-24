"""
Rebuild search index management command.
"""
from django.core.management.base import BaseCommand
from apps.stores.models import Store
from apps.public.search.services import SearchService


class Command(BaseCommand):
    help = 'Rebuild search index'
    
    def add_arguments(self, parser):
        parser.add_argument('--store', type=str, help='Store slug')
    
    def handle(self, *args, **options):
        store_slug = options.get('store')
        
        if store_slug:
            try:
                store = Store.objects.get(slug=store_slug)
                self.stdout.write(f"Rebuilding search index for store: {store.name}")
                
                result = SearchService.rebuild_index(store)
                
                if result:
                    self.stdout.write(self.style.SUCCESS(f"Successfully rebuilt index for {store.name}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Failed to rebuild index for {store.name}"))
                    
            except Store.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Store with slug '{store_slug}' not found"))
        else:
            # Rebuild all stores
            stores = Store.objects.all()
            self.stdout.write(f"Rebuilding search indices for {stores.count()} stores")
            
            for store in stores:
                self.stdout.write(f"Processing store: {store.name}")
                result = SearchService.rebuild_index(store)
                
                if result:
                    self.stdout.write(self.style.SUCCESS(f"✓ {store.name}"))
                else:
                    self.stdout.write(self.style.ERROR(f"✗ {store.name}"))
