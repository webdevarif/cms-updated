"""
Core app configuration for scheduling recurring tasks.
"""
import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    """Core app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Core"

    def ready(self):
        """Called when the app is ready."""
        # Import and schedule recurring tasks
        try:
            from core.background_tasks import sync_translations, warmup_cache
            from core.scheduling import schedule_hourly_task, schedule_weekly_task

            # Schedule hourly cache warmup
            schedule_hourly_task(
                warmup_cache,
                minute=5,  # 5 minutes past the hour
                queue="cache",
                verbose_name="Hourly Cache Warmup",
            )
            logger.info("✅ Scheduled hourly cache warmup at :05 past the hour")

            # Schedule weekly translation sync on Sunday at 4:00 AM
            schedule_weekly_task(
                sync_translations,
                day_of_week=6,  # Sunday (0=Monday, 6=Sunday)
                hour=4,
                minute=0,
                queue="translations",
                verbose_name="Weekly Translation Sync",
            )
            logger.info("✅ Scheduled weekly translation sync on Sunday at 4:00 AM")

        except Exception as e:
            logger.error(f"❌ Failed to schedule core tasks: {e}")
