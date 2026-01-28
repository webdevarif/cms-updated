"""
Clear cache management command.
"""
from apps.cache.services import CacheService
from django.core.cache import cache
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Clear cache"

    def add_arguments(self, parser):
        parser.add_argument("--store", type=str, help="Store slug")
        parser.add_argument("--module", type=str, help="Module name")

    def handle(self, *args, **options):
        store_slug = options.get("store")
        module = options.get("module")

        if store_slug:
            try:
                from apps.stores.models import Store

                store = Store.objects.get(slug=store_slug)

                if module:
                    # Clear specific module for store
                    CacheService.invalidate_module(store, module)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Cleared cache for store '{store_slug}' module '{module}'"
                        )
                    )
                else:
                    # Clear all cache for store
                    CacheService.invalidate_store(store)
                    self.stdout.write(
                        self.style.SUCCESS(f"Cleared all cache for store '{store_slug}'")
                    )

            except Store.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Store with slug '{store_slug}' does not exist")
                )
        else:
            # Clear all cache
            cache.clear()
            self.stdout.write(self.style.SUCCESS("Cleared all cache"))
