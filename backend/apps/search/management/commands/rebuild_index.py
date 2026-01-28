"""
Management command to rebuild search index according to search rules.
"""
from apps.search.services.infrastructure import SearchService
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Rebuild search index for a store"

    def add_arguments(self, parser):
        parser.add_argument("--store", type=str, required=True, help="Store slug or ID")
        parser.add_argument(
            "--force", action="store_true", help="Force rebuild even if index is active"
        )

    def handle(self, *args, **options):
        store_slug = options["store"]
        force = options["force"]

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

            self.stdout.write(f"Rebuilding search index for store: {store.name}")

            # Rebuild index
            success = SearchService.rebuild_index(store)

            if success:
                self.stdout.write(self.style.SUCCESS("✅ Search index rebuilt successfully"))
            else:
                self.stdout.write(self.style.ERROR("❌ Failed to rebuild search index"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
            raise CommandError(f"Rebuild failed: {e}")
