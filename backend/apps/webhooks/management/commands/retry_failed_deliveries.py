"""
Management command to retry failed webhook deliveries.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Retry failed webhook deliveries"

    def add_arguments(self, parser):
        parser.add_argument("--webhook-id", type=int, help="Retry deliveries for specific webhook")

    def handle(self, *args, **options):
        from apps.webhooks.models import WebhookDelivery
        from apps.webhooks.services import WebhookService

        webhook_id = options.get("webhook_id")

        queryset = WebhookDelivery.objects.filter(status="failed")
        if webhook_id:
            queryset = queryset.filter(webhook_id=webhook_id)

        count = 0
        for delivery in queryset:
            WebhookService.schedule_retry(delivery)
            count += 1

        self.stdout.write(f"Scheduled {count} deliveries for retry")
        self.stdout.write(self.style.SUCCESS("Retry complete"))
