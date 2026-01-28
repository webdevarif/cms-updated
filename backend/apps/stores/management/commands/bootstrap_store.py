"""
Management command to bootstrap stores.
"""
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Bootstrap a store or all stores"

    def add_arguments(self, parser):
        parser.add_argument("--slug", type=str, help="Slug of the store to bootstrap")
        parser.add_argument("--all", action="store_true", help="Bootstrap all stores")
        parser.add_argument("--retry", action="store_true", help="Retry failed bootstraps")

    def handle(self, *args, **options):
        from ..models import Store
        from ..services import StoreBootstrapService

        if options["all"]:
            stores = Store.objects.all()
            count = 0
            for store in stores:
                try:
                    StoreBootstrapService.bootstrap_store(store, store.owner)
                    count += 1
                    self.stdout.write(f"Bootstrapped: {store.slug}")
                except Exception as e:
                    self.stdout.write(f"Failed: {store.slug} - {e}")
            self.stdout.write(f"Bootstrapped {count} stores")

        elif options["slug"]:
            try:
                store = Store.objects.get(slug=options["slug"])
                if options["retry"]:
                    result = StoreBootstrapService.retry_bootstrap(store)
                    if result:
                        self.stdout.write(f"Successfully retried bootstrap for: {store.slug}")
                    else:
                        self.stdout.write(f"Bootstrap already completed for: {store.slug}")
                else:
                    StoreBootstrapService.bootstrap_store(store, store.owner)
                    self.stdout.write(f"Successfully bootstrapped: {store.slug}")
            except Store.DoesNotExist:
                self.stdout.write(f'Store not found: {options["slug"]}')

        else:
            self.stdout.write("Please provide --slug or --all option")
