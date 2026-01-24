"""
Warm translation cache management command.
"""
from django.core.management.base import BaseCommand
from django.core.cache import caches
from apps.stores.models import Store
from apps.public.translations.models import Translation
from apps.public.translations.tasks import warm_store_translations
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Warm translation cache for stores'
    
    def add_arguments(self, parser):
        parser.add_argument('--store', type=str, help='Store slug to warm cache for')
        parser.add_argument('--language', type=str, help='Language code to warm cache for')
        parser.add_argument('--async', action='store_true', help='Run warming asynchronously')
    
    def handle(self, *args, **options):
        store_slug = options.get('store')
        language_code = options.get('language')
        async_warming = options.get('async', False)
        
        if store_slug:
            try:
                store = Store.objects.get(slug=store_slug)
                if async_warming:
                    task = warm_store_translations.delay(store.id)
                    self.stdout.write(f"Started async cache warming for store: {store_slug} (task: {task.id})")
                else:
                    self._warm_store_cache(store, language_code)
            except Store.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Store '{store_slug}' not found"))
        else:
            # Warm cache for all stores
            stores = Store.objects.all()
            for store in stores:
                if async_warming:
                    task = warm_store_translations.delay(store.id)
                    self.stdout.write(f"Started async cache warming for store: {store.slug} (task: {task.id})")
                else:
                    self._warm_store_cache(store, language_code)
    
    def _warm_store_cache(self, store, language_code=None):
        """Warm cache for a specific store"""
        cache = caches['translations']
        warmed_count = 0
        
        # Get translations for the store
        translations = Translation.objects.filter(store=store)
        if language_code:
            translations = translations.filter(language__code=language_code)
        
        translations = translations.select_related('key', 'language')
        
        for translation in translations:
            cache_key = f"trans:{store.id}:{translation.language.code}:{translation.key.key}"
            cache.set(cache_key, translation.text, timeout=3600)
            warmed_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Warmed {warmed_count} translations for store: {store.slug}"
                + (f" (language: {language_code})" if language_code else "")
            )
        )
