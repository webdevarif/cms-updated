"""
List queue tasks management command.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'List queue tasks'
    
    def add_arguments(self, parser):
        parser.add_argument('--status', type=str, help='Filter by status (active/scheduled/failed)')
    
    def handle(self, *args, **options):
        status = options.get('status')
        self.stdout.write(f"Listing tasks with status: {status or 'all'}")
        
        # Implementation will go here
        if status:
            self.stdout.write(f"Filtering by status: {status}")
        else:
            self.stdout.write("Listing all tasks")
