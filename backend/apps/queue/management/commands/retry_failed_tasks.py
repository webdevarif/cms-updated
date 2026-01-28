"""
Retry failed tasks management command.
"""
from apps.queue.services import QueueService
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Retry failed queue tasks"

    def add_arguments(self, parser):
        parser.add_argument("--task-id", type=str, help="Specific task ID to retry")

    def handle(self, *args, **options):
        task_id = options.get("task_id")

        if task_id:
            try:
                result = QueueService.retry_task(task_id)
                if result:
                    self.stdout.write(
                        self.style.SUCCESS(f"Successfully initiated retry for task: {task_id}")
                    )
                else:
                    self.stdout.write(self.style.ERROR(f"Failed to retry task: {task_id}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error retrying task {task_id}: {str(e)}"))
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Bulk retry not implemented - use --task-id to retry specific tasks"
                )
            )
            self.stdout.write("Use: python manage.py retry_failed_tasks --task-id=<task_id>")
