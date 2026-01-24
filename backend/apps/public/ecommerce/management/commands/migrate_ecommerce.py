"""
Management command to migrate legacy ecommerce data.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Migrate legacy ecommerce data to new structure'
    
    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be migrated without actually migrating')
        parser.add_argument('--limit', type=int, default=100, help='Limit number of records to migrate')
    
    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        limit = options.get('limit', 100)
        
        self.stdout.write(f"{'[DRY RUN] ' if dry_run else ''}Migrating ecommerce data (limit: {limit})...")
        
        # Migration logic would go here
        # This is a placeholder for actual migration implementation
        
        self.stdout.write(
            self.style.SUCCESS('Ecommerce migration complete')
        )
