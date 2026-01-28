"""
Simple management command for cache warming.
"""
from core.services.cache_service import CacheWarmupService
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Warm cache for a store or all stores"

    def add_arguments(self, parser):
        parser.add_argument("--store", type=str, help="Store slug to warm cache for")
        parser.add_argument("--all", action="store_true", help="Warm cache for all stores")

    def handle(self, *args, **options):
        if options["all"]:
            # Warm cache for all stores
            from apps.stores.models import Store

            stores = Store.objects.all()

            for store in stores:
                success = CacheWarmupService.warm_store_cache(store.slug)
                if success:
                    self.stdout.write(self.style.SUCCESS(f"Warmed cache for store '{store.slug}'"))
                else:
                    self.stdout.write(
                        self.style.ERROR(f"Failed to warm cache for store '{store.slug}'")
                    )

        elif options["store"]:
            store_slug = options["store"]
            success = CacheWarmupService.warm_store_cache(store_slug)
            if success:
                self.stdout.write(self.style.SUCCESS(f"Warmed cache for store '{store_slug}'"))
            else:
                self.stdout.write(
                    self.style.ERROR(f"Failed to warm cache for store '{store_slug}'")
                )
        else:
            self.stdout.write(self.style.ERROR("Please specify --store or --all"))
