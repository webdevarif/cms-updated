"""
Analyze cache management command.
"""
from django.core.management.base import BaseCommand
from apps.cache.services import CacheService


class Command(BaseCommand):
    help = 'Analyze cache performance'
    
    def handle(self, *args, **options):
        self.stdout.write("Analyzing cache performance...")
        
        # Get cache statistics
        stats = CacheService.get_cache_stats()
        
        if 'error' in stats:
            self.stdout.write(
                self.style.ERROR(f"Error getting cache stats: {stats['error']}")
            )
            return
        
        # Display statistics
        self.stdout.write(self.style.SUCCESS("Cache Statistics:"))
        self.stdout.write(f"  Hits: {stats['hits']}")
        self.stdout.write(f"  Misses: {stats['misses']}")
        self.stdout.write(f"  Hit Rate: {stats['hit_rate']:.2f}%")
        
        # Alert if hit rate is low
        if stats['hit_rate'] < 50:
            self.stdout.write(
                self.style.WARNING(f"Low cache hit rate: {stats['hit_rate']:.2f}%")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Good cache hit rate: {stats['hit_rate']:.2f}%")
            )
