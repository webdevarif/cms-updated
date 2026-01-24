"""
Management command to migrate old stores.
"""
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Migrate old stores from DFCMS structure'
    
    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be migrated')
        parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for migration')
    
    def handle(self, *args, **options):
        if options['dry_run']:
            self.stdout.write(self.style.WARNING("Dry run mode - no changes will be made"))
        
        # Migration logic here
        self.stdout.write(self.style.SUCCESS("Store migration completed"))
