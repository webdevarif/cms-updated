"""
Management command to cleanup old notifications.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Clean up old notification records'
    
    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=90, help='Days to keep notifications')
    
    def handle(self, *args, **options):
        days = options.get('days', 90)
        self.stdout.write(f"Cleaning up notifications older than {days} days...")
        
        from ..tasks import cleanup_old_notifications
        deleted_count = cleanup_old_notifications(days=days)
        
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {deleted_count} old notifications')
        )
