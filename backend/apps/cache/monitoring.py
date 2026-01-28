"""
Cache monitoring and alerting system for Digital Farmers CMS.

Real-time cache performance monitoring with alerts.
"""
import json
import logging

from django.core.cache import cache
from django.core.cache.backends.redis import RedisCache
from django.utils import timezone

logger = logging.getLogger(__name__)


class CacheMonitor:
    """Cache monitoring and alerting service"""

    @staticmethod
    def get_detailed_stats():
        """
        Get detailed cache statistics
        """
        if not isinstance(cache, RedisCache):
            return {"error": "Only Redis cache supports detailed stats"}

        client = cache._client
        info = client.info()

        # Get memory usage
        memory_info = client.info("memory")

        # Get key count
        db_info = client.info("keyspace")

        # Calculate hit rate
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total_requests = hits + misses
        hit_rate = (hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "hits": hits,
            "misses": misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
            "memory_used": memory_info.get("used_memory", 0),
            "memory_used_human": CacheMonitor._format_bytes(memory_info.get("used_memory", 0)),
            "memory_peak": memory_info.get("used_memory_peak", 0),
            "memory_peak_human": CacheMonitor._format_bytes(memory_info.get("used_memory_peak", 0)),
            "keyspace_count": db_info.get("keys", 0),
            "expires_count": db_info.get("expires", 0),
            "avg_ttl": db_info.get("avg_ttl", 0),
            "timestamp": timezone.now().isoformat(),
        }

    @staticmethod
    def _format_bytes(bytes_value):
        """Format bytes to human readable format"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"

    @staticmethod
    def check_cache_health():
        """
        Check cache health and return status
        """
        stats = CacheMonitor.get_detailed_stats()

        if "error" in stats:
            return {
                "status": "error",
                "message": stats["error"],
                "timestamp": timezone.now().isoformat(),
            }

        # Health checks
        issues = []

        # Check hit rate
        if stats["hit_rate"] < 50:
            issues.append(
                {
                    "type": "low_hit_rate",
                    "severity": "warning",
                    "message": f"Low cache hit rate: {stats['hit_rate']:.2f}%",
                    "threshold": 50,
                    "current": stats["hit_rate"],
                }
            )
        elif stats["hit_rate"] < 30:
            issues.append(
                {
                    "type": "very_low_hit_rate",
                    "severity": "critical",
                    "message": f"Very low cache hit rate: {stats['hit_rate']:.2f}%",
                    "threshold": 30,
                    "current": stats["hit_rate"],
                }
            )

        # Check memory usage
        memory_usage_percent = (
            (stats["memory_used"] / stats["memory_peak"]) * 100 if stats["memory_peak"] > 0 else 0
        )
        if memory_usage_percent > 80:
            issues.append(
                {
                    "type": "high_memory_usage",
                    "severity": "warning",
                    "message": f"High memory usage: {memory_usage_percent:.2f}%",
                    "threshold": 80,
                    "current": memory_usage_percent,
                }
            )
        elif memory_usage_percent > 95:
            issues.append(
                {
                    "type": "very_high_memory_usage",
                    "severity": "critical",
                    "message": f"Very high memory usage: {memory_usage_percent:.2f}%",
                    "threshold": 95,
                    "current": memory_usage_percent,
                }
            )

        # Check key count
        if stats["keyspace_count"] > 100000:
            issues.append(
                {
                    "type": "high_key_count",
                    "severity": "warning",
                    "message": f"High key count: {stats['keyspace_count']}",
                    "threshold": 100000,
                    "current": stats["keyspace_count"],
                }
            )

        # Determine overall status
        if any(issue["severity"] == "critical" for issue in issues):
            status = "critical"
        elif any(issue["severity"] == "warning" for issue in issues):
            status = "warning"
        else:
            status = "healthy"

        return {
            "status": status,
            "stats": stats,
            "issues": issues,
            "timestamp": timezone.now().isoformat(),
        }

    @staticmethod
    def get_top_keys(limit=10):
        """
        Get top cache keys by size or access frequency
        """
        if not isinstance(cache, RedisCache):
            return {"error": "Only Redis cache supports key analysis"}

        client = cache._client

        # Get all keys with their sizes
        keys_info = []

        # Sample keys (in production, you might want to use SCAN instead of KEYS)
        all_keys = client.keys("cms:*")

        for key in all_keys[:limit]:
            try:
                key_info = client.debug_object(key)
                keys_info.append(
                    {
                        "key": key.decode("utf-8"),
                        "size": key_info.get("serializedlength", 0),
                        "size_human": CacheMonitor._format_bytes(
                            key_info.get("serializedlength", 0)
                        ),
                        "type": key_info.get("encoding", "unknown"),
                        "ttl": key_info.get("ttl", -1),
                    }
                )
            except:
                keys_info.append(
                    {
                        "key": key.decode("utf-8"),
                        "size": 0,
                        "size_human": "0 B",
                        "type": "unknown",
                        "ttl": -1,
                    }
                )

        # Sort by size
        keys_info.sort(key=lambda x: x["size"], reverse=True)

        return keys_info

    @staticmethod
    def log_cache_metrics():
        """
        Log cache metrics for monitoring
        """
        stats = CacheMonitor.get_detailed_stats()

        if "error" in stats:
            logger.error(f"Cache monitoring error: {stats['error']}")
            return

        # Log key metrics
        logger.info(
            f"Cache Metrics - Hits: {stats['hits']}, Misses: {stats['misses']}, "
            f"Hit Rate: {stats['hit_rate']:.2f}%, Keys: {stats['keyspace_count']}, "
            f"Memory: {stats['memory_used_human']}"
        )

        # Log alerts for issues
        health = CacheMonitor.check_cache_health()

        if health["status"] != "healthy":
            for issue in health["issues"]:
                if issue["severity"] == "critical":
                    logger.error(f"Cache Alert - {issue['message']}")
                else:
                    logger.warning(f"Cache Warning - {issue['message']}")

    @staticmethod
    def get_store_cache_stats(store_slug):
        """
        Get cache statistics for a specific store
        """
        if not isinstance(cache, RedisCache):
            return {"error": "Only Redis cache supports store-specific stats"}

        client = cache._client

        # Build pattern for store keys
        pattern = f"cms:{store_slug}:*"
        keys = client.keys(pattern)

        if not keys:
            return {
                "store_slug": store_slug,
                "key_count": 0,
                "estimated_size": 0,
                "estimated_size_human": "0 B",
            }

        # Calculate total size
        total_size = 0
        for key in keys:
            try:
                key_info = client.debug_object(key)
                total_size += key_info.get("serializedlength", 0)
            except:
                pass

        return {
            "store_slug": store_slug,
            "key_count": len(keys),
            "estimated_size": total_size,
            "estimated_size_human": CacheMonitor._format_bytes(total_size),
            "timestamp": timezone.now().isoformat(),
        }


class CacheAlertManager:
    """Cache alerting system"""

    @staticmethod
    def check_and_alert():
        """
        Check cache health and send alerts if needed
        """
        health = CacheMonitor.check_cache_health()

        if health["status"] == "critical":
            # Send critical alert
            CacheAlertManager._send_alert(
                level="critical",
                title="Cache Critical Alert",
                message=f"Cache system has critical issues: {len(health['issues'])} issues detected",
                details=health["issues"],
            )
        elif health["status"] == "warning":
            # Send warning alert
            CacheAlertManager._send_alert(
                level="warning",
                title="Cache Warning",
                message=f"Cache system has warnings: {len(health['issues'])} issues detected",
                details=health["issues"],
            )

        return health

    @staticmethod
    def _send_alert(level, title, message, details):
        """
        Send cache alert (placeholder for email/slack/webhook integration)
        """
        # Log the alert
        if level == "critical":
            logger.error(f"CRITICAL: {title} - {message}")
            for detail in details:
                logger.error(f"  - {detail['message']}")
        else:
            logger.warning(f"WARNING: {title} - {message}")
            for detail in details:
                logger.warning(f"  - {detail['message']}")

        # TODO: Integrate with notification system
        # This could send emails, Slack messages, webhooks, etc.
        # from apps.notifications.services import NotificationService
        # NotificationService.send_alert(level, title, message, details)
