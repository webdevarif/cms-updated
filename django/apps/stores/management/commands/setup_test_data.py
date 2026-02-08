"""
Management command to create test membership for development.
"""
from apps.stores.models import Store, StoreMembership

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create test membership for development user and store"

    def handle(self, *args, **options):
        try:
            # Get or create test user
            user, created = User.objects.get_or_create(
                username="testuser",
                defaults={"email": "test@example.com", "first_name": "Test", "last_name": "User"},
            )
            if created:
                user.set_password("testpass123")
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created test user: {user.username}"))

            # Get or create test store
            store, created = Store.objects.get_or_create(
                name="Test Store",
                defaults={
                    "owner": user,
                    "description": "A test store for development",
                    "status": "active",
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created test store: {store.name} (ID: {store.id})")
                )

            # Create membership if it doesn't exist
            membership, created = StoreMembership.objects.get_or_create(
                user=user, store=store, defaults={"role": "owner"}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created membership: {user.username} -> {store.name} (role: {membership.role})"
                    )
                )
            else:
                self.stdout.write(
                    f"Membership already exists: {user.username} -> {store.name} (role: {membership.role})"
                )

            self.stdout.write(self.style.SUCCESS("Test data setup complete"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error setting up test data: {e}"))
