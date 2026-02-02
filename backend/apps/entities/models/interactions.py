"""
Entity interaction models for entities app.
"""

from core.models import TenantModel
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

User = get_user_model()


class EntityInteraction(TenantModel):
    """
    User interactions with entities (likes, votes, etc.)
    Generic relationship to any model
    """

    # Relationships
    action = models.ForeignKey(
        "entities.EntityAction", on_delete=models.CASCADE, related_name="interactions"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="entity_interactions",
        null=True,
        blank=True,
    )

    # Generic foreign key to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

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

    class Meta(TenantModel.Meta):
        db_table = "entities_entity_interaction"
        unique_together = [["store", "action", "user", "content_type", "object_id"]]
        indexes = [
            models.Index(fields=["action", "content_type", "object_id"]),
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} {self.action.name} {self.content_object}"
