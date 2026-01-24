"""
Base services for centralized ORM operations.
"""
from django.db import transaction
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class BaseTenantCRUDService:
    """
    Base service for tenant-scoped CRUD operations with centralized ORM handling
    """
    
    model_class = None
    
    @classmethod
    def create(cls, store=None, **kwargs):
        """
        Centralized create method with tenant scoping
        
        Args:
            store: Store instance for tenant scoping
            **kwargs: Model field values
            
        Returns:
            Created model instance
        """
        if not cls.model_class:
            raise NotImplementedError("model_class must be defined")
        
        if store and hasattr(cls.model_class, 'store'):
            kwargs['store'] = store
        
        try:
            return cls.model_class.objects.create(**kwargs)
        except Exception as e:
            logger.error(f"Error creating {cls.model_class.__name__}: {str(e)}")
            raise ValidationError(f"Error creating {cls.model_class.__name__}: {str(e)}")
    
    @classmethod
    def get(cls, **kwargs):
        """
        Centralized get method
        
        Args:
            **kwargs: Filter criteria
            
        Returns:
            Model instance or raises DoesNotExist
        """
        if not cls.model_class:
            raise NotImplementedError("model_class must be defined")
        
        return cls.model_class.objects.get(**kwargs)
    
    @classmethod
    def filter(cls, **kwargs):
        """
        Centralized filter method
        
        Args:
            **kwargs: Filter criteria
            
        Returns:
            QuerySet
        """
        if not cls.model_class:
            raise NotImplementedError("model_class must be defined")
        
        return cls.model_class.objects.filter(**kwargs)
    
    @classmethod
    def update(cls, instance, **kwargs):
        """
        Centralized update method
        
        Args:
            instance: Model instance to update
            **kwargs: Fields to update
            
        Returns:
            Updated instance
        """
        if not instance:
            raise ValueError("Instance is required")
        
        for field, value in kwargs.items():
            if hasattr(instance, field):
                setattr(instance, field, value)
        
        instance.save()
        return instance
    
    @classmethod
    def delete(cls, instance):
        """
        Centralized delete method
        
        Args:
            instance: Model instance to delete
            
        Returns:
            Tuple of (deleted_count, deleted_objects)
        """
        if not instance:
            raise ValueError("Instance is required")
        
        return instance.delete()


class GiftCardQueryHelper:
    """
    Helper for gift card analytics and queries
    """
    
    @staticmethod
    def get_store_analytics(store, start_date=None, end_date=None):
        """
        Get analytics for gift cards in a store
        
        Args:
            store: Store instance
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            dict: Analytics data
        """
        from apps.public.giftcards.models import GiftCard, GiftCardHistory
        from django.db.models import Sum, Count, Q
        from django.utils import timezone
        
        end_date = end_date or timezone.now()
        filters = Q(store=store)
        
        if start_date:
            filters &= Q(created_at__range=(start_date, end_date))
        
        # Basic stats
        stats = {
            'total_gift_cards': GiftCard.objects.filter(filters).count(),
            'active_gift_cards': GiftCard.objects.filter(
                filters & Q(status='active')
            ).count(),
            'total_value': GiftCard.objects.filter(
                filters & Q(status='active')
            ).aggregate(Sum('current_balance'))['current_balance__sum'] or 0,
        }
        
        return stats


class LogQueryHelper:
    """
    Helper for log analytics and queries
    """
    
    @staticmethod
    def get_store_analytics(store, days=30):
        """
        Get analytics for logs in a store
        
        Args:
            store: Store instance
            days: Number of days to look back
            
        Returns:
            dict: Analytics data
        """
        from apps.logs.models import LogEntry
        from django.utils import timezone
        from django.db.models import Count
        
        since = timezone.now() - timezone.timedelta(days=days)
        
        # Basic metrics
        total_visits = LogEntry.objects.filter(
            store=store,
            event_type='PAGE_VIEW',
            created_at__gte=since
        ).count()
        
        unique_visitors = LogEntry.objects.filter(
            store=store,
            event_type='PAGE_VIEW',
            created_at__gte=since
        ).values('session_id').distinct().count()
        
        return {
            'total_visits': total_visits,
            'unique_visitors': unique_visitors,
            'period_days': days,
        }


class MediaCRUDService(BaseTenantCRUDService):
    """
    CRUD service for MediaFile operations
    """
    model_class = None  # Will be set dynamically
    
    @classmethod
    def create_media_file(cls, **kwargs):
        """Create MediaFile with proper validation"""
        from apps.mediafile.models.media_file import MediaFile
        cls.model_class = MediaFile
        return cls.create(**kwargs)
    
    @classmethod
    def get_media_file(cls, **kwargs):
        """Get MediaFile by criteria"""
        from apps.mediafile.models.media_file import MediaFile
        cls.model_class = MediaFile
        return cls.get(**kwargs)
    
    @classmethod
    def filter_media_files(cls, **kwargs):
        """Filter MediaFile by criteria"""
        from apps.mediafile.models.media_file import MediaFile
        cls.model_class = MediaFile
        return cls.filter(**kwargs)
    
    @classmethod
    def delete_media_file(cls, instance):
        """Delete MediaFile with cleanup"""
        return cls.delete(instance)


class ValidationHelper:
    """
    Helper class for common validation patterns
    """
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number format"""
        import re
        pattern = r'^[\d\s\-\+\(\)]+$'
        if not re.match(pattern, phone):
            return False
        # Remove all non-digit characters and check length
        digits = re.sub(r'\D', '', phone)
        return len(digits) >= 10
    
    @staticmethod
    def validate_url(url):
        """Validate URL format"""
        from django.core.validators import URLValidator
        validator = URLValidator()
        try:
            validator(url)
            return True
        except:
            return False
    
    @staticmethod
    def sanitize_string(text, max_length=None, allow_html=False):
        """Sanitize string input"""
        if not text:
            return ""
        
        if not allow_html:
            import bleach
            text = bleach.clean(text)
        
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        return text.strip()


class CacheHelper:
    """
    Helper class for cache operations
    """
    
    @staticmethod
    def get_cache_key(prefix, *args):
        """Generate consistent cache key"""
        from django.utils.hash import md5
        key_string = f"{prefix}:{':'.join(str(arg) for arg in args)}"
        return f"dfcms_{md5(key_string.encode()).hexdigest()}"
    
    @staticmethod
    def cache_get(key, default=None):
        """Get value from cache with error handling"""
        try:
            from django.core.cache import cache
            return cache.get(key, default)
        except:
            return default
    
    @staticmethod
    def cache_set(key, value, timeout=300):
        """Set value in cache with error handling"""
        try:
            from django.core.cache import cache
            cache.set(key, value, timeout)
            return True
        except:
            return False
    
    @staticmethod
    def cache_delete(key):
        """Delete value from cache with error handling"""
        try:
            from django.core.cache import cache
            cache.delete(key)
            return True
        except:
            return False


class SecurityHelper:
    """
    Helper class for security-related operations
    """
    
    @staticmethod
    def generate_token(length=32):
        """Generate secure random token"""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def hash_password(password):
        """Hash password using Django's default hasher"""
        from django.contrib.auth.hashers import make_password
        return make_password(password)
    
    @staticmethod
    def verify_password(password, hashed):
        """Verify password against hash"""
        from django.contrib.auth.hashers import check_password
        return check_password(password, hashed)
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def is_suspicious_ip(ip_address):
        """Check if IP address is in suspicious list"""
        # This would integrate with a security service or database
        # For now, return False (not suspicious)
        return False
