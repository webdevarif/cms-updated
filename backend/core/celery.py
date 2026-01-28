"""
Celery configuration for the Digital Farmers CMS.
"""
import os

from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")

app = Celery("core")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure Celery to use Redis as broker and result backend
app.conf.update(
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_send_sent_event=True,
    task_send_failure_event=True,
    task_send_retry_event=True,
    worker_send_task_events=True,
)

# Optional: Configure beat schedule
app.conf.beat_schedule = getattr(settings, "CELERY_BEAT_SCHEDULE", {})


@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery functionality."""
    print(f"Request: {self.request!r}")
    return f"Debug task executed: {self.request.id}"
