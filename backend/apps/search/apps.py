"""App configuration for search module."""
import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class SearchConfig(AppConfig):
    label = "search"
    """App config for search app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.search"
    verbose_name = "Search"

    def ready(self):
        """Called when the app is ready."""
        # Import and schedule recurring tasks
        try:
            from core.background_tasks import rebuild_search_index
            from core.scheduling import schedule_daily_task

            # Schedule daily search index rebuild at 3:00 AM
            schedule_daily_task(
                rebuild_search_index,
                hour=3,
                minute=0,
                queue="search",
                verbose_name="Daily Search Index Rebuild",
            )
            logger.info("✅ Scheduled daily search index rebuild at 3:00 AM")

        except Exception as e:
            logger.error(f"❌ Failed to schedule search tasks: {e}")
