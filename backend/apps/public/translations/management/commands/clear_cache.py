"""
Clear translation cache management command.
"""
from django.core.management.base import BaseCommand
from django.core.cache import caches
from apps.stores.models import Store
from apps.public.translations.tasks import clear_translation_cache
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Clear translation cache'
    
    def add_arguments(self, parser):
        parser.add_argument('--store', type=str, help='Store slug to clear cache for')
        parser.add_argument('--language', type=str, help='Language code to clear cache for')
        parser.add_argument('--async', action='store_true', help='Run clearing asynchronously')
    
    def handle(self, *args, **options):
        store_slug = options.get('store')
        language_code = options.get('language')
        async_clearing = options.get('async', False)
        
        if store_slug:
            try:
                store = Store.objects.get(slug=store_slug)
                if async_clearing:
                    task = clear_translation_cache.delay(store.id, language_code)
                    self.stdout.write(f"Started async cache clearing for store: {store_slug} (task: {task.id})")
                else:
                    self._clear_cache(store.id, language_code)
            except Store.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Store '{store_slug}' not found"))
        else:
            # Clear all cache
            if async_clearing:
                task = clear_translation_cache.delay(None, language_code)
                self.stdout.write(f"Started async cache clearing for all stores (task: {task.id})")
            else:
                self._clear_cache(None, language_code)
    
    def _clear_cache(self, store_id=None, language_code=None):
        """Clear cache synchronously"""
        cache = caches['translations']
        
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("translations")
            
            # Build cache key pattern
            if store_id and language_code:
                pattern = f"trans:{store_id}:{language_code}:*"
            elif store_id:
                pattern = f"trans:{store_id}:*"
            elif language_code:
                pattern = f"trans:*:{language_code}:*"
            else:
                pattern = "trans:*"
            
            # Find and delete keys
            keys = redis_conn.keys(pattern)
            if keys:
                redis_conn.delete(*keys)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Cleared {len(keys)} translation cache entries"
                        + (f" for store_id: {store_id}" if store_id else "")
                        + (f" (language: {language_code})" if language_code else "")
                    )
                )
            else:
                self.stdout.write("No translation cache entries found")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to clear cache: {e}"))
