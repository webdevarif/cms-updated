"""
Entity analytics service for entities app.

Provides analytics and statistics for entity actions and interactions.
"""

from django.db.models import Avg, Count


def get_action_stats(entity_action):
    """
    Get comprehensive statistics for an entity action.

    Args:
        entity_action: EntityAction instance

    Returns:
        dict: Statistics including counts, ratings, content type distribution, and recent interactions
    """
    from ..models.interactions import EntityInteraction

    interactions = EntityInteraction.objects.filter(action=entity_action)

    stats = {
        "total_interactions": interactions.count(),
        "active_interactions": interactions.filter(is_active=True).count(),
        "unique_users": interactions.values("user").distinct().count(),
        "average_rating": interactions.filter(rating__isnull=False).aggregate(
            avg_rating=Avg("rating")
        )["avg_rating"]
        or 0,
        "interactions_by_content_type": list(
            interactions.values("content_type__model")
            .annotate(count=Count("id"))
            .order_by("-count")
        ),
        "recent_interactions": list(
            interactions.filter(is_active=True)
            .order_by("-created_at")[:10]
            .values(
                "user__username",
                "content_type__model",
                "object_id",
                "rating",
                "created_at",
            )
        ),
    }

    return stats


def get_interaction_summary(entity_action):
    """
    Get basic interaction summary for an entity action.

    Args:
        entity_action: EntityAction instance

    Returns:
        dict: Basic counts and user statistics
    """
    from ..models.interactions import EntityInteraction

    interactions = EntityInteraction.objects.filter(action=entity_action)

    return {
        "total_interactions": interactions.count(),
        "active_interactions": interactions.filter(is_active=True).count(),
        "unique_users": interactions.values("user").distinct().count(),
    }


def get_content_type_distribution(entity_action):
    """
    Get distribution of interactions by content type.

    Args:
        entity_action: EntityAction instance

    Returns:
        list: Content types with interaction counts
    """
    from ..models.interactions import EntityInteraction

    return list(
        EntityInteraction.objects.filter(action=entity_action)
        .values("content_type__model")
        .annotate(count=Count("id"))
        .order_by("-count")
    )


def get_recent_interactions(entity_action, limit=10):
    """
    Get recent interactions for an entity action.

    Args:
        entity_action: EntityAction instance
        limit: Number of recent interactions to return

    Returns:
        list: Recent interaction data
    """
    from ..models.interactions import EntityInteraction

    return list(
        EntityInteraction.objects.filter(action=entity_action, is_active=True)
        .order_by("-created_at")[:limit]
        .values("user__username", "content_type__model", "object_id", "rating", "created_at")
    )
