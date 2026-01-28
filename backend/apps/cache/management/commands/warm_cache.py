"""
Warm cache management command.
"""
from apps.cache.services import CacheWarmupService
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Warm cache"

    def add_arguments(self, parser):
        parser.add_argument("--store", type=str, help="Store slug")

    def handle(self, *args, **options):
        store_slug = options.get("store")

        if store_slug:
            try:
                from apps.stores.models import Store

                store = Store.objects.get(slug=store_slug)

                # Warm cache for specific store
                CacheWarmupService.warm_store_cache(store)
                self.stdout.write(self.style.SUCCESS(f"Cache warmed for store '{store_slug}'"))

            except Store.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Store with slug '{store_slug}' does not exist")
                )
        else:
            # Warm cache for all stores
            from apps.stores.models import Store

            stores = Store.objects.all()

            for store in stores:
                CacheWarmupService.warm_store_cache(store)

            self.stdout.write(self.style.SUCCESS(f"Cache warmed for {stores.count()} stores"))
