"""
Management command to cleanup old webhook deliveries.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Clean up old webhook delivery records'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Number of days to keep deliveries (default: 90)'
        )
    
    def handle(self, *args, **options):
        from apps.webhooks.models import WebhookDelivery
        
        days = options['days']
        cutoff = timezone.now() - timezone.timedelta(days=days)
        
        count, _ = WebhookDelivery.objects.filter(
            triggered_at__lt=cutoff,
            status='success'
        ).delete()
        
        self.stdout.write(f'Deleted {count} old webhook deliveries')
        self.stdout.write(self.style.SUCCESS('Cleanup complete'))
