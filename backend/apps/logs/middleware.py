"""
Logging middleware for automatic request logging.
"""
import time
import uuid
from django.utils import timezone
from .models import LogEntry
from .tasks import log_event_async


class LoggingMiddleware:
    """Middleware to automatically log page views and API calls"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip static files and admin
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return self.get_response(request)
        
        # Generate request ID
        request.request_id = str(uuid.uuid4())
        start_time = time.time()
        
        response = self.get_response(request)
        
        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Log page view asynchronously
        log_data = {
            'event_type': 'PAGE_VIEW',
            'level': 'INFO',
            'message': f"Page view: {request.path}",
            'store': getattr(request, 'store', None),
            'user': request.user if request.user.is_authenticated else None,
            'session_id': request.session.session_key,
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'request_id': request.request_id,
            'page_url': request.build_absolute_uri(),
            'referrer': request.META.get('HTTP_REFERER', ''),
            'duration_ms': duration_ms,
            'metadata': {
                'method': request.method,
                'status_code': response.status_code,
                'query_params': dict(request.GET),
            }
        }
        
        # Use async for performance - TEMPORARILY DISABLED
        # log_event_async.delay(log_data)
        
        # TODO: Re-enable async logging when Celery is configured
        # For now, log synchronously to avoid connection errors
        try:
            from .models import LogEntry
            LogEntry.objects.create(**log_data)
        except Exception as e:
            # Silently fail to avoid breaking the application
            pass
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
