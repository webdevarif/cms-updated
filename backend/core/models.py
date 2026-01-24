"""
Core models for Digital Farmers CMS.

This module contains base models that are used across all apps.
"""
from django.db import models


class TenantModel(models.Model):
    """
    Base model for all tenant-scoped models.
    
    All models that are scoped to a store/tenant should inherit from this model.
    It provides a store field and common metadata.
    """
    store = models.ForeignKey(
        'stores.Store',
        on_delete=models.CASCADE,
        related_name='%(class)ss'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['store']),
        ]
