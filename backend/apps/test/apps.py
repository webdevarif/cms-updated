"""
Apps configuration for test module.
"""
import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class TestConfig(AppConfig):
    label = "test"
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.test"
    verbose_name = "Test"

    def ready(self):
        """Called when the app is ready."""
        # Import and schedule recurring tasks
        try:
            from core.background_tasks import run_full_test_suite
            from core.scheduling import schedule_daily_task

            # Schedule nightly full test suite at 1:00 AM
            schedule_daily_task(
                run_full_test_suite,
                hour=1,
                minute=0,
                queue="test",
                verbose_name="Nightly Full Test Suite",
            )
            logger.info("✅ Scheduled nightly full test suite at 1:00 AM")

        except Exception as e:
            logger.error(f"❌ Failed to schedule test tasks: {e}")
