import logging
from datetime import timedelta

from core.services.base import BaseTenantCRUDService

from django.db import transaction
from django.db.models import Avg, Count
from django.utils import timezone

from ..models.events import EventLog

logger = logging.getLogger(__name__)


class EventService:
    @staticmethod
    def log_event(
        event_type,
        event_name,
        properties=None,
        request=None,
        user=None,
        store=None,
        duration_ms=None,
    ):
        log_data = {
            "event_type": event_type,
            "event_name": event_name,
            "properties": properties or {},
            "user": user,
            "store": store,
            "session_id": (request.session.session_key if request and request.session else None),
            "ip_address": request.META.get("REMOTE_ADDR") if request else None,
            "user_agent": request.META.get("HTTP_USER_AGENT", "") if request else "",
            "request_id": str(request.id) if request and hasattr(request, "id") else "",
            "duration_ms": duration_ms,
        }
        BaseTenantCRUDService.model_class = EventLog
        return BaseTenantCRUDService.create(**log_data)

    @staticmethod
    def log_search(query, results_count, duration_ms=None, request=None, user=None, store=None):
        from ..models.events import SearchLog

        search_data = {
            "query": query,
            "results_count": results_count,
            "success": True,
            "search_type": "content",
            "user": user,
            "store": store,
            "session_id": (request.session.session_key if request and request.session else None),
            "ip_address": request.META.get("REMOTE_ADDR") if request else None,
            "duration_ms": duration_ms,
        }

        # Create SearchLog record
        search_log = SearchLog.objects.create(**search_data)

        # Also log as event for unified tracking
        properties = {
            "query": query,
            "results_count": results_count,
            "duration_ms": duration_ms,
        }
        return EventService.log_event(
            "SEARCH_QUERY", f"Search: {query}", properties, request, user, store
        )

    @staticmethod
    def log_page_view(request, user=None, store=None, duration_ms=None):
        if request:
            event_name = f"Page View: {request.path}"
            properties = {
                "page_url": request.build_absolute_uri(),
                "referrer": request.META.get("HTTP_REFERER", ""),
                "duration_ms": duration_ms,
            }
        else:
            event_name = "Page View: Unknown"
            properties = {"duration_ms": duration_ms}
        return EventService.log_event(
            "PAGE_VIEW", event_name, properties, request, user, store, duration_ms
        )

    @staticmethod
    def log_user_action(action_name, properties=None, request=None, user=None, store=None):
        event_name = f"User Action: {action_name}"
        properties = properties or {}
        return EventService.log_event("USER_ACTION", event_name, properties, request, user, store)

    @staticmethod
    def get_store_analytics(store, days=30):
        since = timezone.now() - timedelta(days=days)
        event_logs = EventLog.objects.filter(store=store, created_at__gte=since)
        total_events = event_logs.count()
        event_distribution = (
            event_logs.values("event_type").annotate(count=Count("id")).order_by("-count")[:10]
        )
        # Simplified analytics; adapt as needed based on EventLog fields
        return {
            "total_events": total_events,
            "event_distribution": list(event_distribution),
            "period_days": days,
        }

    @staticmethod
    def detect_suspicious_activity(store, hours=24):
        since = timezone.now() - timedelta(hours=hours)
        suspicious_events = EventLog.objects.filter(
            store=store,
            event_type__in=["LOGIN_FAILED", "SUSPICIOUS_ACTIVITY"],
            created_at__gte=since,
        ).count()  # Simplified detection
        return suspicious_events

    @staticmethod
    def get_entity_history(store, entity_type, entity_id, days=30):
        since = timezone.now() - timedelta(days=days)
        events = EventLog.objects.filter(
            store=store,
            event_name__icontains=entity_type,
            properties__has_key="entity_id",
            created_at__gte=since,
        ).order_by(
            "-created_at"
        )  # Approximate match based on event_name or properties
        return list(events)

    @staticmethod
    def get_user_activity(store, user, days=30):
        since = timezone.now() - timedelta(days=days)
        events = EventLog.objects.filter(store=store, user=user, created_at__gte=since).order_by(
            "-created_at"
        )
        activity_summary = (
            events.values("event_type").annotate(count=Count("id")).order_by("-count")
        )
        return {
            "total_activities": events.count(),
            "activities": list(events[:50]),
            "summary": list(activity_summary),
            "period_days": days,
        }

    @staticmethod
    def cleanup_old_logs(store=None, days=90):
        cutoff = timezone.now() - timedelta(days=days)
        filters = {"created_at__lt": cutoff}
        if store:
            filters["store"] = store
        deleted_count = EventLog.objects.filter(**filters).delete()[0]
        return {
            "deleted_count": deleted_count,
            "cutoff_date": cutoff.isoformat(),
            "store": store.name if store else "all_stores",
        }

    @staticmethod
    def get_real_time_metrics(store, minutes=5):
        since = timezone.now() - timedelta(minutes=minutes)
        events = EventLog.objects.filter(store=store, created_at__gte=since)
        total_requests = events.count()
        page_views = events.filter(event_type="PAGE_VIEW").count()
        errors = events.filter(
            event_type__in=["ERROR", "CRITICAL"]
        ).count()  # Adapt based on event_type mapping
        suspicious = events.filter(event_type="SUSPICIOUS_ACTIVITY").count()
        avg_response_time = (
            events.filter(event_type="PAGE_VIEW", duration_ms__isnull=False).aggregate(
                avg=Avg("duration_ms")
            )["avg"]
            or 0
        )
        return {
            "total_requests": total_requests,
            "page_views": page_views,
            "errors": errors,
            "suspicious": suspicious,
            "avg_response_time_ms": round(avg_response_time, 2),
            "requests_per_minute": round(total_requests / minutes, 2),
            "error_rate": round((errors / total_requests * 100) if total_requests > 0 else 0, 2),
            "period_minutes": minutes,
        }

    @staticmethod
    def export_logs(store, format="csv", days=30, event_types=None):
        since = timezone.now() - timedelta(days=days)
        filters = {"store": store, "created_at__gte": since}
        if event_types:
            filters["event_type__in"] = event_types
        events = EventLog.objects.filter(**filters).order_by("-created_at")
        if format == "csv":
            import csv
            from io import StringIO

            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(
                [
                    "id",
                    "event_type",
                    "event_name",
                    "user_email",
                    "ip_address",
                    "created_at",
                ]
            )
            for event in events:
                user_email = event.user.email if event.user else ""
                writer.writerow(
                    [
                        event.id,
                        event.event_type,
                        event.event_name,
                        user_email,
                        event.ip_address,
                        event.created_at.isoformat(),
                    ]
                )
            return output.getvalue()
        elif format == "json":
            import json

            data = [
                {
                    "id": event.id,
                    "event_type": event.event_type,
                    "event_name": event.event_name,
                    "user_email": event.user.email if event.user else None,
                    "ip_address": event.ip_address,
                    "created_at": event.created_at.isoformat(),
                    "properties": event.properties,
                }
                for event in events
            ]
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def get_system_status():
        from django.db.models import Count

        latest_event = EventLog.objects.order_by("-created_at").first()
        if latest_event and latest_event.event_type == "SYSTEM_STARTUP":
            return {
                "status": "running",
                "message": "System is operational",
                "timestamp": latest_event.created_at.isoformat(),
                "total_logs": EventLog.objects.count(),
                "error_count": EventLog.objects.filter(event_type="SYSTEM_ERROR").count(),
            }
        else:
            return {
                "status": "unknown",
                "message": "No recent system events",
                "timestamp": None,
                "total_logs": 0,
                "error_count": 0,
            }
