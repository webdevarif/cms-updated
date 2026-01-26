"""
Infrastructure search models according to search rules.
"""
from django.db import models
from core.models import TenantModel


class SearchIndex(TenantModel):
    """
    INFRASTRUCTURE: Store-scoped search index configuration
    """
    
    # Core fields - INFRASTRUCTURE PROVIDES
    name = models.CharField(max_length=255)
    index_name = models.CharField(max_length=255, unique=True, db_index=True)
    
    # Index configuration - INFRASTRUCTURE PROVIDES
    content_types = models.JSONField(
        default=list,
        help_text="List of content types to index: ['Page', 'Post', 'Product']"
    )
    
    # Search configuration - INFRASTRUCTURE PROVIDES
    fields = models.JSONField(
        default=dict,
        help_text="Field mappings and search configuration"
    )
    
    # Facet configuration - INFRASTRUCTURE PROVIDES
    facets = models.JSONField(
        default=list,
        help_text="Facet configuration for filtering"
    )
    
    # Status - INFRASTRUCTURE PROVIDES
    is_active = models.BooleanField(default=True)
    last_reindexed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta(TenantModel.Meta):
        db_table = 'search_index'
        unique_together = [['store', 'name']]
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.index_name}"
    
    def get_index_name(self):
        """INFRASTRUCTURE PROVIDES: Full index name with store prefix"""
        return f"{self.store.slug}_{self.index_name}"


class SearchQuery(TenantModel):
    """
    INFRASTRUCTURE: Track search queries for analytics
    """
    
    # Core fields - INFRASTRUCTURE PROVIDES
    query = models.CharField(max_length=255, db_index=True)
    
    # Search context - INFRASTRUCTURE PROVIDES
    search_type = models.CharField(
        max_length=50,
        choices=[
            ('content', 'Content'),
            ('product', 'Product'),
            ('all', 'All')
        ]
    )
    
    # Results - INFRASTRUCTURE PROVIDES
    results_count = models.PositiveIntegerField(default=0)
    
    # User tracking - INFRASTRUCTURE PROVIDES
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    session_id = models.CharField(max_length=100, blank=True)
    
    # Filters applied - INFRASTRUCTURE PROVIDES
    filters = models.JSONField(default=dict)
    
    # Timing - INFRASTRUCTURE PROVIDES
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta(TenantModel.Meta):
        db_table = 'search_query'
        indexes = [
            models.Index(fields=['store', 'query']),
            models.Index(fields=['created_at']),
            models.Index(fields=['search_type']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.query} - {self.results_count} results"
