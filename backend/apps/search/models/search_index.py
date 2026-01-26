"""Search index models for unified search functionality."""
from django.db import models
from django.contrib.postgres.indexes import GinIndex


class SearchResult(models.Model):
    """
    Cached search results for performance optimization.
    Stores pre-computed search results for common queries.
    """
    query = models.CharField(max_length=255, db_index=True)
    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cached_search_results"
    )
    content_type = models.CharField(max_length=50)  # e.g., 'product', 'post', 'page'
    object_id = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    excerpt = models.TextField(blank=True)
    url = models.URLField(max_length=500)
    score = models.FloatField(default=0.0)
    metadata = models.JSONField(default=dict, blank=True)  # Additional searchable data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-score', '-updated_at']
        indexes = [
            models.Index(fields=['query', 'store']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['score']),
        ]
        unique_together = [['query', 'store', 'content_type', 'object_id']]
    
    def __str__(self):
        return f"{self.title} ({self.content_type})"
