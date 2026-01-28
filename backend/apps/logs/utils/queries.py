"""
Centralized log query operations.
"""
from apps.logs.models import LogEntry
from django.db.models import Count


class LogQueryHelper:
    """Centralized log query operations"""

    @staticmethod
    def get_base_query(store, since=None, event_type=None):
        """Get base query with common filters"""
        queryset = LogEntry.objects.filter(store=store)
        if since:
            queryset = queryset.filter(created_at__gte=since)
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        return queryset

    @staticmethod
    def get_page_view_stats(store, since=None):
        """Get page view statistics"""
        base_query = LogQueryHelper.get_base_query(store, since, "PAGE_VIEW")

        return {
            "total_visits": base_query.count(),
            "unique_visitors": base_query.values("session_id").distinct().count(),
            "top_pages": list(
                base_query.values("page_url").annotate(views=Count("id")).order_by("-views")[:10]
            ),
        }

    @staticmethod
    def get_bounce_rate(store, since=None):
        """Calculate bounce rate"""
        base_query = LogQueryHelper.get_base_query(store, since, "PAGE_VIEW")

        total_sessions = base_query.values("session_id").distinct().count()
        bounce_sessions = (
            base_query.values("session_id")
            .annotate(page_views=Count("id"))
            .filter(page_views=1)
            .count()
        )

        return (bounce_sessions / total_sessions * 100) if total_sessions > 0 else 0

    @staticmethod
    def detect_suspicious_patterns(store, since=None, threshold=5):
        """Detect suspicious activity patterns"""
        base_query = LogQueryHelper.get_base_query(store, since)

        # Failed logins
        failed_logins = (
            base_query.filter(event_type="LOGIN_FAILED")
            .values("ip_address")
            .annotate(count=Count("id"))
            .filter(count__gt=threshold)
        )

        # Rapid requests
        rapid_requests = (
            base_query.filter(event_type="PAGE_VIEW")
            .values("ip_address")
            .annotate(count=Count("id"))
            .filter(count__gt=1000)
        )

        return {"failed_logins": list(failed_logins), "rapid_requests": list(rapid_requests)}
