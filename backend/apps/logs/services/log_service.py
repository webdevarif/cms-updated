"""
Services for logs app.
"""
from datetime import timedelta
from django.db.models import Count, Q, Avg
from django.utils import timezone
from apps.logs.models import LogEntry


class LogService:
    """Service for log analytics and queries"""
    
    @staticmethod
    def log_event(store, event_type, message='', user=None, **kwargs):
        """
        Log an event with centralized service
        
        Args:
            store: Store instance
            event_type: Event type string
            message: Optional message
            user: Optional user instance
            **kwargs: Additional log data
            
        Returns:
            LogEntry: Created log entry
        """
        from core.services.base import BaseTenantCRUDService
        
        log_data = {
            'store': store,
            'event_type': event_type,
            'level': kwargs.get('level', 'INFO'),
            'message': message,
            'user': user,
            'ip_address': kwargs.get('ip_address'),
            'user_agent': kwargs.get('user_agent', ''),
            'request_id': kwargs.get('request_id', ''),
            'entity_type': kwargs.get('entity_type', ''),
            'entity_id': kwargs.get('entity_id'),
            'metadata': kwargs.get('metadata', {}),
            'page_url': kwargs.get('page_url', ''),
            'referrer': kwargs.get('referrer', ''),
            'duration_ms': kwargs.get('duration_ms'),
            'is_suspicious': kwargs.get('is_suspicious', False),
            'risk_score': kwargs.get('risk_score', 0),
        }
        
        BaseTenantCRUDService.model_class = LogEntry
        return BaseTenantCRUDService.create(**log_data)
    
    @staticmethod
    def get_store_analytics(store, days=30):
        """Get analytics for a store"""
        since = timezone.now() - timedelta(days=days)
        
        # Use centralized query helpers
        from .utils.queries import LogQueryHelper
        page_stats = LogQueryHelper.get_page_view_stats(store, since)
        bounce_rate = LogQueryHelper.get_bounce_rate(store, since)
        suspicious = LogQueryHelper.detect_suspicious_patterns(store, since)
        
        # Security events
        security_events = LogQueryHelper.get_base_query(
            store, since
        ).filter(is_suspicious=True).count()
        
        # Event type distribution
        event_distribution = LogQueryHelper.get_base_query(
            store, since
        ).values('event_type').annotate(count=Count('id')).order_by('-count')[:10]
        
        # User activity
        user_activity = LogQueryHelper.get_base_query(
            store, since
        ).values('user__email').annotate(count=Count('id')).exclude(user__isnull=True).order_by('-count')[:10]
        
        return {
            'total_visits': page_stats['total_visits'],
            'unique_visitors': page_stats['unique_visitors'],
            'bounce_rate': round(bounce_rate, 2),
            'top_pages': page_stats['top_pages'],
            'security_events': security_events,
            'event_distribution': list(event_distribution),
            'user_activity': list(user_activity),
            'period_days': days,
        }
    
    @staticmethod
    def detect_suspicious_activity(store, hours=24):
        """Detect suspicious patterns"""
        since = timezone.now() - timedelta(hours=hours)
        from .utils.queries import LogQueryHelper
        return LogQueryHelper.detect_suspicious_patterns(store, since)
    
    @staticmethod
    def get_user_activity(store, user, days=30):
        """
        Get activity for a specific user
        
        Args:
            store: Store instance
            user: User instance
            days: Number of days to look back
            
        Returns:
            dict: User activity data
        """
        since = timezone.now() - timedelta(days=days)
        
        from core.services.base import BaseTenantCRUDService
        BaseTenantCRUDService.model_class = LogEntry
        
        activities = BaseTenantCRUDService.filter(
            store=store,
            user=user,
            created_at__gte=since
        ).order_by('-created_at')
        
        # Activity summary
        activity_summary = activities.values('event_type').annotate(count=Count('id')).order_by('-count')
        
        return {
            'total_activities': activities.count(),
            'activities': list(activities[:50]),  # Last 50 activities
            'summary': list(activity_summary),
            'period_days': days,
        }
    
    @staticmethod
    def get_entity_history(store, entity_type, entity_id, days=30):
        """
        Get history for a specific entity
        
        Args:
            store: Store instance
            entity_type: Entity type (e.g., 'Product', 'Order')
            entity_id: Entity ID
            days: Number of days to look back
            
        Returns:
            list: Entity history
        """
        since = timezone.now() - timedelta(days=days)
        
        from core.services.base import BaseTenantCRUDService
        BaseTenantCRUDService.model_class = LogEntry
        
        return list(BaseTenantCRUDService.filter(
            store=store,
            entity_type=entity_type,
            entity_id=entity_id,
            created_at__gte=since
        ).order_by('-created_at'))
    
    @staticmethod
    def cleanup_old_logs(store=None, days=90):
        """
        Clean up old logs to prevent table bloat
        
        Args:
            store: Optional store to filter by (None for all stores)
            days: Number of days to keep
            
        Returns:
            dict: Cleanup results
        """
        from core.services.base import BaseTenantCRUDService
        BaseTenantCRUDService.model_class = LogEntry
        
        cutoff = timezone.now() - timedelta(days=days)
        
        filters = {'created_at__lt': cutoff}
        if store:
            filters['store'] = store
        
        deleted_count = BaseTenantCRUDService.filter(**filters).delete()[0]
        
        return {
            'deleted_count': deleted_count,
            'cutoff_date': cutoff.isoformat(),
            'store': store.name if store else 'all_stores',
        }
    
    @staticmethod
    def export_logs(store, format='csv', days=30, event_types=None):
        """
        Export logs for a store
        
        Args:
            store: Store instance
            format: Export format ('csv' or 'json')
            days: Number of days to export
            event_types: Optional list of event types to filter by
            
        Returns:
            str: Exported data
        """
        since = timezone.now() - timedelta(days=days)
        
        from core.services.base import BaseTenantCRUDService
        BaseTenantCRUDService.model_class = LogEntry
        
        filters = {
            'store': store,
            'created_at__gte': since
        }
        
        if event_types:
            filters['event_type__in'] = event_types
        
        logs = BaseTenantCRUDService.filter(**filters).order_by('-created_at')
        
        if format == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                'id', 'event_type', 'level', 'message', 'user_email',
                'ip_address', 'created_at', 'entity_type', 'entity_id'
            ])
            
            # Data
            for log in logs:
                writer.writerow([
                    log.id, log.event_type, log.level, log.message,
                    log.user.email if log.user else '',
                    log.ip_address, log.created_at.isoformat(),
                    log.entity_type, log.entity_id
                ])
            
            return output.getvalue()
        
        elif format == 'json':
            import json
            
            data = []
            for log in logs:
                data.append({
                    'id': log.id,
                    'event_type': log.event_type,
                    'level': log.level,
                    'message': log.message,
                    'user_email': log.user.email if log.user else None,
                    'ip_address': log.ip_address,
                    'created_at': log.created_at.isoformat(),
                    'entity_type': log.entity_type,
                    'entity_id': log.entity_id,
                    'metadata': log.metadata,
                })
            
            return json.dumps(data, indent=2)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    @staticmethod
    def get_real_time_metrics(store, minutes=5):
        """
        Get real-time metrics for the last N minutes
        
        Args:
            store: Store instance
            minutes: Number of minutes to look back
            
        Returns:
            dict: Real-time metrics
        """
        since = timezone.now() - timedelta(minutes=minutes)
        
        from core.services.base import BaseTenantCRUDService
        BaseTenantCRUDService.model_class = LogEntry
        
        recent_logs = BaseTenantCRUDService.filter(
            store=store,
            created_at__gte=since
        )
        
        # Calculate metrics
        total_requests = recent_logs.count()
        page_views = recent_logs.filter(event_type='PAGE_VIEW').count()
        errors = recent_logs.filter(level__in=['ERROR', 'CRITICAL']).count()
        suspicious = recent_logs.filter(is_suspicious=True).count()
        
        # Average response time for page views
        avg_response_time = recent_logs.filter(
            event_type='PAGE_VIEW',
            duration_ms__isnull=False
        ).aggregate(avg=Avg('duration_ms'))['avg'] or 0
        
        return {
            'total_requests': total_requests,
            'page_views': page_views,
            'errors': errors,
            'suspicious': suspicious,
            'avg_response_time_ms': round(avg_response_time, 2),
            'requests_per_minute': round(total_requests / minutes, 2),
            'error_rate': round((errors / total_requests * 100) if total_requests > 0 else 0, 2),
            'period_minutes': minutes,
        }
