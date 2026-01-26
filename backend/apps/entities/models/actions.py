"""
Entity action models for entities app.
"""
from django.db import models
from core.models import TenantModel


class EntityAction(TenantModel):
    """
    Store-scoped entity actions (Like, Heart, Upvote, DownVote, etc.)
    Defines available actions for content types
    """
    
    # Core fields
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    description = models.TextField(blank=True)
    
    # Action configuration
    ACTION_TYPES = [
        ('toggle', 'Toggle (Like/Unlike)'),
        ('single', 'Single (Upvote only)'),
        ('rating', 'Rating (1-5 stars)'),
        ('counter', 'Counter (View count)'),
    ]
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES, default='toggle')
    
    # Visual configuration
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=20, blank=True)
    
    # Content type targeting
    content_types = models.JSONField(
        default=list,
        help_text="Which models this action applies to"
    )
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    allow_anonymous = models.BooleanField(default=False)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta(TenantModel.Meta):
        db_table = 'entities_entity_action'
        unique_together = [['store', 'slug']]
        indexes = [
            models.Index(fields=['store', 'is_active']),
            models.Index(fields=['content_types']),
        ]
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.action_type})"
