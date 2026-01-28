"""
Simple management commands for cache operations.
"""
from core.services.cache_service import CacheService, CacheWarmupService
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Clear cache for a store or all stores"

    def add_arguments(self, parser):
        parser.add_argument("--store", type=str, help="Store slug to clear cache for")
        parser.add_argument("--all", action="store_true", help="Clear all cache")

    def handle(self, *args, **options):
        if options["all"]:
            # Clear all cache using django-redis
            from django.core.cache import cache

            cache.clear()
            self.stdout.write(self.style.SUCCESS("Cleared all cache"))
        elif options["store"]:
            store_slug = options["store"]
            success = CacheService.invalidate_store(store_slug)
            if success:
                self.stdout.write(self.style.SUCCESS(f"Cleared cache for store '{store_slug}'"))
            else:
                self.stdout.write(
                    self.style.ERROR(f"Failed to clear cache for store '{store_slug}'")
                )
        else:
            self.stdout.write(self.style.ERROR("Please specify --store or --all"))
