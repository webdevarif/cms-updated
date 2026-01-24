"""
Cache models.
"""
from django.db import models


class CacheEntry(models.Model):
    """
    Store-scoped cache entry
    """
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    key = models.CharField(max_length=255, db_index=True)
    value = models.JSONField()
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cache_entry'
        unique_together = [['store', 'key']]
        indexes = [
            models.Index(fields=['store', 'key']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.key}"
    
    def is_expired(self):
        from django.utils import timezone
        return self.expires_at and timezone.now() > self.expires_at

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_value = None
        
        if not is_new:
            old_instance = CacheEntry.objects.get(pk=self.pk)
            old_value = old_instance.value
        
        super().save(*args, **kwargs)
        
        from apps.logs.tasks import log_event_async
        
        if is_new:
            log_event_async.delay({
                'event_type': 'create_cacheentry_public_cache',
                'message': f"Cache entry created: {self.key}",
                'store_id': self.store.id,
                'object_id': self.id,
                'metadata': {
                    'key': self.key,
                    'expires_at': self.expires_at.isoformat() if self.expires_at else None
                }
            })
        elif old_value != self.value:
            log_event_async.delay({
                'event_type': 'update_cacheentry_public_cache',
                'message': f"Cache entry updated: {self.key}",
                'store_id': self.store.id,
                'object_id': self.id,
                'metadata': {
                    'key': self.key,
                    'expires_at': self.expires_at.isoformat() if self.expires_at else None
                }
            })
