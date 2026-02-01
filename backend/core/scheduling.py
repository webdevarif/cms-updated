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


def schedule_daily_task(
    task_func, hour=0, minute=0, args=None, kwargs=None, queue="default", verbose_name=None
):
    """Schedule a daily recurring task."""
    try:
        # Calculate next run time
        now = timezone.now()
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # If the time has already passed today, schedule for tomorrow
        if next_run <= now:
            next_run += timezone.timedelta(days=1)

        # Schedule the task
        task = task_func(args=args or [], kwargs=kwargs or [], queue=queue, schedule=next_run)

        task_name = verbose_name or task_func.__name__
        logger.info(f"Scheduled daily task '{task_name}' at {hour:02d}:{minute:02d}")
        return task

    except Exception as e:
        logger.error(f"Failed to schedule daily task: {e}")
        raise


def schedule_hourly_task(
    task_func, minute=0, args=None, kwargs=None, queue="default", verbose_name=None
):
    """Schedule an hourly recurring task."""
    try:
        # Calculate next run time
        now = timezone.now()
        next_run = now.replace(minute=minute, second=0, microsecond=0)

        # If the time has already passed this hour, schedule for next hour
        if next_run <= now:
            next_run += timezone.timedelta(hours=1)

        # Schedule the task
        task = task_func(args=args or [], kwargs=kwargs or [], queue=queue, schedule=next_run)

        task_name = verbose_name or task_func.__name__
        logger.info(f"Scheduled hourly task '{task_name}' at minute {minute}")
        return task

    except Exception as e:
        logger.error(f"Failed to schedule hourly task: {e}")
        raise


def schedule_weekly_task(
    task_func,
    day_of_week=0,
    hour=0,
    minute=0,
    args=None,
    kwargs=None,
    queue="default",
    verbose_name=None,
):
    """Schedule a weekly recurring task."""
    try:
        # Calculate next run time
        now = timezone.now()
        days_ahead = (day_of_week - now.weekday() + 7) % 7
        if days_ahead == 0 and now.time() > timezone.time(hour, minute):
            days_ahead = 7

        next_run = now + timezone.timedelta(days=days_ahead)
        next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # Schedule the task
        task = task_func(args=args or [], kwargs=kwargs or [], queue=queue, schedule=next_run)

        task_name = verbose_name or task_func.__name__
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        logger.info(
            f"Scheduled weekly task '{task_name}' on {day_names[day_of_week]} at {hour:02d}:{minute:02d}"
        )
        return task

    except Exception as e:
        logger.error(f"Failed to schedule weekly task: {e}")
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
