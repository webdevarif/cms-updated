"""
Models for entities app.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class EntityAction(models.Model):
    """
    Store-scoped entity actions (Like, Heart, Upvote, DownVote, etc.)
    Defines available actions for content types
    """
    
    # Store scoping
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    
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
    
    class Meta:
        db_table = 'entities_entity_action'
        unique_together = [['store', 'slug']]
        indexes = [
            models.Index(fields=['store', 'is_active']),
            models.Index(fields=['store', 'action_type']),
        ]
        ordering = ['store', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.action_type})"


class EntityInteraction(models.Model):
    """
    User interactions with entities (likes, votes, etc.)
    Generic relationship to any model
    """
    
    # Store scoping
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    
    # Relationships
    action = models.ForeignKey(
        'EntityAction',
        on_delete=models.CASCADE,
        related_name='interactions'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='entity_interactions',
        null=True,
        blank=True
    )
    
    # Generic foreign key to any model
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Interaction data
    value = models.JSONField(default=dict, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'entities_entity_interaction'
        unique_together = [
            ['store', 'action', 'user', 'content_type', 'object_id']
        ]
        indexes = [
            models.Index(fields=['store', 'action', 'created_at']),
            models.Index(fields=['action', 'content_type', 'object_id']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} {self.action.name} {self.content_object}"
