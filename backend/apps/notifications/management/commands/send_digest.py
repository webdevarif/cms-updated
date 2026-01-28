"""
Management command to send digest notifications.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Send digest notifications for users with digest enabled"

    def handle(self, *args, **options):
        self.stdout.write("Sending digest notifications...")

        from ..tasks import send_digest_notifications

        send_digest_notifications()

        self.stdout.write(self.style.SUCCESS("Digest notifications sent"))
