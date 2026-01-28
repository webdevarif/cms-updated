"""
Simple scheduling helpers for background tasks.
"""
import logging

from django.utils import timezone

logger = logging.getLogger(__name__)


def schedule_task(task_name, args=None, kwargs=None, delay_seconds=0, queue="default"):
    """Schedule a background task to run after a delay."""
    try:
        # Import the task function directly
        module_path, function_name = task_name.rsplit(".", 1)
        module = __import__(module_path, fromlist=[function_name])
        task_func = getattr(module, function_name)

        # Calculate run time
        run_at = timezone.now() + timezone.timedelta(seconds=delay_seconds)

        # Schedule the task
        task = task_func(args=args or [], kwargs=kwargs or [], queue=queue, schedule=run_at)

        logger.info(f"Scheduled task '{task_name}' to run in {delay_seconds} seconds")
        return task

    except Exception as e:
        logger.error(f"Failed to schedule task '{task_name}': {e}")
        raise


def schedule_daily(task_name, hour=0, minute=0, args=None, kwargs=None, queue="default"):
    """Schedule a daily recurring task."""
    try:
        # Calculate next run time
        now = timezone.now()
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # If the time has already passed today, schedule for tomorrow
        if next_run <= now:
            next_run += timezone.timedelta(days=1)

        # Import and schedule task
        module_path, function_name = task_name.rsplit(".", 1)
        module = __import__(module_path, fromlist=[function_name])
        task_func = getattr(module, function_name)

        task = task_func(args=args or [], kwargs=kwargs or [], queue=queue, schedule=next_run)

        logger.info(f"Scheduled daily task '{task_name}' at {hour:02d}:{minute:02d}")
        return task

    except Exception as e:
        logger.error(f"Failed to schedule daily task '{task_name}': {e}")
        raise


def schedule_hourly(task_name, minute=0, args=None, kwargs=None, queue="default"):
    """Schedule an hourly recurring task."""
    try:
        # Calculate next run time
        now = timezone.now()
        next_run = now.replace(minute=minute, second=0, microsecond=0)

        # If the time has already passed this hour, schedule for next hour
        if next_run <= now:
            next_run += timezone.timedelta(hours=1)

        # Import and schedule task
        module_path, function_name = task_name.rsplit(".", 1)
        module = __import__(module_path, fromlist=[function_name])
        task_func = getattr(module, function_name)

        task = task_func(args=args or [], kwargs=kwargs or [], queue=queue, schedule=next_run)

        logger.info(f"Scheduled hourly task '{task_name}' at minute {minute}")
        return task

    except Exception as e:
        logger.error(f"Failed to schedule hourly task '{task_name}': {e}")
        raise


# Common scheduling shortcuts
def schedule_daily_cache_warmup():
    """Schedule daily cache warmup at 2:00 AM."""
    return schedule_daily("apps.core.tasks.warmup_cache", hour=2, minute=0, queue="search")


def schedule_daily_search_rebuild():
    """Schedule daily search index rebuild at 2:30 AM."""
    return schedule_daily("apps.core.tasks.rebuild_search_index", hour=2, minute=30, queue="search")


def schedule_hourly_search_optimization():
    """Schedule hourly search optimization."""
    return schedule_hourly("apps.core.tasks.optimize_search_indices", minute=0, queue="search")


def schedule_test_suite(app_label=None):
    """Schedule test suite to run immediately."""
    return schedule_task(
        "apps.core.tasks.run_app_tests", args=[app_label], delay_seconds=60, queue="test"
    )


def schedule_full_test_suite():
    """Schedule full test suite to run immediately."""
    return schedule_task("apps.core.tasks.run_full_test_suite", delay_seconds=60, queue="test")
