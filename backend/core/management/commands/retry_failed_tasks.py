"""
Retry failed Celery tasks management command.
"""

from celery import current_app
from celery.result import AsyncResult
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Retry failed Celery tasks command"""

    help = "Retry failed Celery tasks"

    def add_arguments(self, parser):
        parser.add_argument("--task-id", type=str, help="Specific task ID to retry")

    def handle(self, *args, **options):
        """Handle command execution"""
        task_id = options.get("task_id")

        if task_id:
            try:
                result = AsyncResult(task_id)

                if result.failed():
                    # Get the original task name and arguments
                    task_name = None
                    task_args = []
                    task_kwargs = {}

                    # Try to extract task info from the result
                    if hasattr(result, "args") and result.args:
                        task_args = result.args
                    if hasattr(result, "kwargs") and result.kwargs:
                        task_kwargs = result.kwargs

                    # Revoke the failed task first
                    current_app.control.revoke(task_id, terminate=False)

                    # Re-enqueue the task
                    if task_name:
                        new_task = current_app.send_task(
                            task_name, args=task_args, kwargs=task_kwargs
                        )
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Successfully initiated retry for task: {task_id} -> {new_task.id}"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Could not determine task name for retry: {task_id}"
                            )
                        )
                else:
                    self.stdout.write(self.style.WARNING(f"Task {task_id} is not in failed state"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error retrying task {task_id}: {str(e)}"))
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Bulk retry not implemented - use --task-id to retry specific tasks"
                )
            )
            self.stdout.write("Use: python manage.py retry_failed_tasks --task-id=<task_id>")
