"""
Cache admin interface.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import Cache, CacheStats


@admin.register(Cache)
class CacheAdmin(admin.ModelAdmin):
    """Admin interface for cache entries"""

    list_display = [
        'key_short', 'cache_type', 'store', 'content_type',
        'hits', 'misses', 'hit_ratio_display', 'is_expired',
        'updated_at'
    ]
    list_filter = ['cache_type', 'store', 'content_type', 'is_expired']
    search_fields = ['key', 'content_type', 'object_id']
    readonly_fields = ['created_at', 'updated_at', 'hits', 'misses']
    ordering = ['-updated_at']

    def key_short(self, obj):
        """Display shortened cache key"""
        return obj.key[:50] + '...' if len(obj.key) > 50 else obj.key
    key_short.short_description = 'Cache Key'

    def hit_ratio_display(self, obj):
        """Display hit ratio as percentage"""
        ratio = obj.hit_ratio
        color = 'green' if ratio > 80 else 'orange' if ratio > 50 else 'red'
        return format_html('<span style="color: {};">{:.1f}%</span>', color, ratio)
    hit_ratio_display.short_description = 'Hit Ratio'

    def has_add_permission(self, request):
        """Disable adding cache entries manually"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deletion of cache entries"""
        return True

    actions = ['clear_selected_cache', 'invalidate_by_tags']

    def clear_selected_cache(self, request, queryset):
        """Clear selected cache entries"""
        count = queryset.count()
        for cache_entry in queryset:
            # Invalidate actual cache
            from .services import CacheService
            CacheService.invalidate_key(cache_entry.key, cache_entry.store)

        self.message_user(request, f'Successfully cleared {count} cache entries.')
    clear_selected_cache.short_description = 'Clear selected cache entries'

    def invalidate_by_tags(self, request, queryset):
        """Invalidate cache entries by their tags"""
        tags = set()
        for cache_entry in queryset:
            tags.update(cache_entry.tags)

        # Invalidate by tags
        from .services import CacheService
        for tag in tags:
            CacheService.invalidate_by_tag(tag)

        self.message_user(request, f'Invalidated cache entries with tags: {", ".join(tags)}')
    invalidate_by_tags.short_description = 'Invalidate by tags'


@admin.register(CacheStats)
class CacheStatsAdmin(admin.ModelAdmin):
    """Admin interface for cache statistics"""

    list_display = [
        'store', 'interval', 'period_start', 'total_keys',
        'hit_ratio_display', 'memory_usage_display', 'total_hits', 'total_misses'
    ]
    list_filter = ['interval', 'store', 'period_start']
    readonly_fields = [
        'store', 'interval', 'period_start', 'total_keys', 'total_size_bytes',
        'expired_keys', 'total_hits', 'total_misses', 'avg_response_time_ms',
        'page_cache_hits', 'api_cache_hits', 'query_cache_hits', 'fragment_cache_hits',
        'memory_used_bytes', 'memory_available_bytes', 'cpu_usage_percent',
        'connections_active', 'created_at'
    ]
    ordering = ['-period_start']

    def hit_ratio_display(self, obj):
        """Display hit ratio as percentage"""
        ratio = obj.hit_ratio
        color = 'green' if ratio > 80 else 'orange' if ratio > 50 else 'red'
        return format_html('<span style="color: {};">{:.1f}%</span>', color, ratio)
    hit_ratio_display.short_description = 'Hit Ratio'

    def memory_usage_display(self, obj):
        """Display memory usage as percentage"""
        usage = obj.memory_usage_percent
        color = 'red' if usage > 90 else 'orange' if usage > 75 else 'green'
        return format_html('<span style="color: {};">{:.1f}%</span>', color, usage)
    memory_usage_display.short_description = 'Memory Usage'

    def has_add_permission(self, request):
        """Disable adding stats manually"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deletion of old stats"""
        return True
