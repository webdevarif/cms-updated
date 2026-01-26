"""
Cache models for performance monitoring and management.
"""
from django.db import models
from django.utils import timezone
from datetime import timedelta


class Cache(models.Model):
    """Cache entry model for monitoring cached content"""

    CACHE_TYPES = [
        ('page', 'Page Cache'),
        ('fragment', 'Fragment Cache'),
        ('query', 'Query Cache'),
        ('api', 'API Cache'),
        ('session', 'Session Cache'),
        ('template', 'Template Cache'),
    ]

    key = models.CharField(max_length=500, db_index=True, help_text="Cache key")
    cache_type = models.CharField(max_length=20, choices=CACHE_TYPES, default='page', db_index=True)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='cache_entries')

    # Content information
    content_type = models.CharField(max_length=100, blank=True, help_text="Type of cached content")
    object_id = models.CharField(max_length=100, blank=True, help_text="ID of cached object")
    tags = models.JSONField(default=list, blank=True, help_text="Cache tags for selective invalidation")

    # Performance metrics
    size_bytes = models.PositiveIntegerField(null=True, blank=True, help_text="Approximate size in bytes")
    hits = models.PositiveIntegerField(default=0, help_text="Number of cache hits")
    misses = models.PositiveIntegerField(default=0, help_text="Number of cache misses")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="When cache entry expires")

    class Meta:
        db_table = 'cache_entry'
        unique_together = [['store', 'key']]
        indexes = [
            models.Index(fields=['store', 'cache_type']),
            models.Index(fields=['store', 'expires_at']),
            models.Index(fields=['store', 'updated_at']),
            models.Index(fields=['cache_type', 'updated_at']),
        ]
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.cache_type}: {self.key[:50]}..."

    @property
    def is_expired(self):
        """Check if cache entry is expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @property
    def hit_ratio(self):
        """Calculate cache hit ratio"""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0

    def increment_hit(self):
        """Increment hit counter"""
        self.hits += 1
        self.save(update_fields=['hits', 'updated_at'])

    def increment_miss(self):
        """Increment miss counter"""
        self.misses += 1
        self.save(update_fields=['misses', 'updated_at'])


class CacheStats(models.Model):
    """Cache performance statistics"""

    INTERVAL_CHOICES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='cache_stats')
    interval = models.CharField(max_length=20, choices=INTERVAL_CHOICES, default='hourly')
    period_start = models.DateTimeField(db_index=True)

    # Overall statistics
    total_keys = models.PositiveIntegerField(default=0)
    total_size_bytes = models.PositiveBigIntegerField(default=0)
    expired_keys = models.PositiveIntegerField(default=0)

    # Performance metrics
    total_hits = models.PositiveIntegerField(default=0)
    total_misses = models.PositiveIntegerField(default=0)
    avg_response_time_ms = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    # Cache type breakdown
    page_cache_hits = models.PositiveIntegerField(default=0)
    api_cache_hits = models.PositiveIntegerField(default=0)
    query_cache_hits = models.PositiveIntegerField(default=0)
    fragment_cache_hits = models.PositiveIntegerField(default=0)

    # Memory usage
    memory_used_bytes = models.PositiveBigIntegerField(default=0)
    memory_available_bytes = models.PositiveBigIntegerField(default=0)

    # System metrics
    cpu_usage_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    connections_active = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cache_stats'
        unique_together = [['store', 'interval', 'period_start']]
        indexes = [
            models.Index(fields=['store', 'interval', 'period_start']),
            models.Index(fields=['interval', 'period_start']),
            models.Index(fields=['store', 'created_at']),
        ]
        ordering = ['-period_start']

    def __str__(self):
        return f"{self.store.name} - {self.interval} - {self.period_start}"

    @property
    def hit_ratio(self):
        """Calculate overall hit ratio"""
        total = self.total_hits + self.total_misses
        return (self.total_hits / total * 100) if total > 0 else 0

    @property
    def memory_usage_percent(self):
        """Calculate memory usage percentage"""
        total = self.memory_used_bytes + self.memory_available_bytes
        return (self.memory_used_bytes / total * 100) if total > 0 else 0
