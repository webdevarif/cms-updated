"""
Cache statistics dashboard view for monitoring Redis cache performance.
"""
from core.services.cache_service import CacheService
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods


@method_decorator([login_required], name="dispatch")
class CacheStatsView(View):
    """
    Simple dashboard view for cache statistics.
    """

    def get(self, request):
        """Get cache statistics for the current store"""
        if not hasattr(request, "store") or not request.store:
            return JsonResponse({"error": "Store context required"}, status=400)

        # Get store-specific stats
        store_stats = CacheService.get_store_stats(request.store.slug)

        # Get global stats (only for admin users)
        global_stats = {}
        if request.user.is_staff or request.user.is_superuser:
            global_stats = CacheService.get_global_stats()

        return JsonResponse(
            {
                "store_stats": store_stats,
                "global_stats": global_stats if global_stats else None,
                "cache_backend": "Redis"
                if hasattr(CacheService.get_store_stats.__func__, "__globals__").get("cache")
                and str(type(CacheService.get_store_stats.__func__.__globals__["cache"]))
                else "Unknown",
            }
        )


@require_http_methods(["POST"])
@login_required
def clear_store_cache(request):
    """Clear all cache for the current store"""
    if not hasattr(request, "store") or not request.store:
        return JsonResponse({"error": "Store context required"}, status=400)

    try:
        success = CacheService.invalidate_store(request.store.slug)
        if success:
            return JsonResponse({"message": f"Cache cleared for store {request.store.slug}"})
        else:
            return JsonResponse({"error": "Failed to clear cache - Redis required"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["POST"])
@login_required
def warm_store_cache(request):
    """Warm cache for the current store"""
    if not hasattr(request, "store") or not request.store:
        return JsonResponse({"error": "Store context required"}, status=400)

    try:
        from core.services.cache_service import CacheWarmupService

        success = CacheWarmupService.warm_store_cache(request.store.slug)
        if success:
            return JsonResponse({"message": f"Cache warmed for store {request.store.slug}"})
        else:
            return JsonResponse({"error": "Cache warming failed"}, status=500)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
