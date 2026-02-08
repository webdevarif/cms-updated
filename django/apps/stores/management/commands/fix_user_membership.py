"""
Management command to fix user membership for store access.
"""
from apps.stores.models import Store, StoreMembership

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Fix user membership for store access"

    def handle(self, *args, **options):
        try:
            # Get test user
            u = User.objects.get(username="testuser")
            self.stdout.write(f"Found user: {u.username}")

            # Check store 8 (what frontend sends)
            try:
                store = Store.objects.get(id=8)
                self.stdout.write(f"Found store 8: {store.name} (owner: {store.owner.username})")

                # Check if user has membership
                membership = StoreMembership.objects.filter(user=u, store=store).first()

                if membership:
                    self.stdout.write(
                        f"User already has membership in store 8: role {membership.role}"
                    )
                else:
                    # Create membership for owner
                    if store.owner == u:
                        membership = StoreMembership.objects.create(
                            user=u, store=store, role="owner"
                        )
                        self.stdout.write(
                            self.style.SUCCESS(f"Created owner membership for user in store 8")
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"User is not owner of store 8 - cannot create membership"
                            )
                        )

            except Store.DoesNotExist:
                self.stdout.write(self.style.ERROR("Store 8 does not exist"))

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("Test user does not exist"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
