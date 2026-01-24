"""
Search models for CMS.
"""
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class SearchIndex(models.Model):
    """
    Store-scoped search index configuration
    """
    # Store scoping
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    
    # Core fields
    name = models.CharField(max_length=100)
    index_name = models.CharField(max_length=100)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    auto_update = models.BooleanField(default=True)
    
    # Index settings
    max_results = models.PositiveIntegerField(default=100)
    boost_recent = models.BooleanField(default=True)
    
    # Content types to index
    content_types = models.ManyToManyField(ContentType, related_name='search_indexes')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'search_index'
        unique_together = [['store', 'name']]
        indexes = [
            models.Index(fields=['store', 'is_active']),
            models.Index(fields=['store', 'index_name']),
        ]
        ordering = ['name']
    
    def __str__(self):
        return f"{self.store.slug}_{self.index_name}"


class SearchQuery(models.Model):
    """
    Track search queries for analytics
    """
    # Store scoping
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    
    # Query details
    query = models.CharField(max_length=255, db_index=True)
    results_count = models.PositiveIntegerField(default=0)
    
    # User context
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Search context
    index_used = models.CharField(max_length=100, blank=True)
    filters = models.JSONField(default=dict, blank=True)
    
    # Performance
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'search_query'
        indexes = [
            models.Index(fields=['store', 'created_at']),
            models.Index(fields=['store', 'query']),
            models.Index(fields=['store', 'user']),
            models.Index(fields=['query']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.query} ({self.results_count} results)"


class SearchDocument(models.Model):
    """
    Store-scoped search document (legacy - kept for backward compatibility)
    """
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    search_index = models.ForeignKey(SearchIndex, on_delete=models.CASCADE, related_name='documents')
    
    # Generic relation to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Search data
    title = models.CharField(max_length=255)
    content = models.TextField()
    metadata = models.JSONField(default=dict, help_text="Additional searchable metadata")
    
    # Status
    is_indexed = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'search_document'
        unique_together = [['search_index', 'content_type', 'object_id']]
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['title']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
