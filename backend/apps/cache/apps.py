"""
Apps configuration for cache
Cache app configuration for Digital Farmers CMS.
"""
from django.apps import AppConfig


class CacheConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cache'
    verbose_name = 'Cache Management'
    
    def ready(self):
        """Import cache signals for automatic cache management"""
        try:
            from . import signals
            from . import monitoring
            
            # Start cache monitoring if Celery is available
            try:
                from .tasks import schedule_cache_monitoring
                # Schedule monitoring to start after app is ready
                import threading
                import time
                
                def start_monitoring():
                    time.sleep(10)  # Wait for app to fully start
                    try:
                        schedule_cache_monitoring.delay()
                    except:
                        pass  # Celery might not be available
                
                thread = threading.Thread(target=start_monitoring, daemon=True)
                thread.start()
                
            except ImportError:
                # Celery not available - skip monitoring
                pass
                
        except ImportError:
            # Signals or monitoring modules not available
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("Cache signals or monitoring modules not found - some features may not work")
