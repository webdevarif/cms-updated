"""
Tasks for queue module.
"""
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def example_task(self, *args, **kwargs):
    """
    Example task with retry logic
    """
    try:
        # Task logic here
        result = perform_operation(*args, **kwargs)

        logger.info(f"Task completed successfully: {self.request.id}")
        return result

    except Exception as exc:
        logger.error(f"Task failed: {exc}")

        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


def perform_operation(*args, **kwargs):
    """Placeholder operation - queue task handler"""
    # This is a placeholder for queue operations
    # In production, this would handle specific queue tasks
    import logging

    logger = logging.getLogger(__name__)
    logger.info(f"Queue operation performed with args: {args}, kwargs: {kwargs}")
    return True
