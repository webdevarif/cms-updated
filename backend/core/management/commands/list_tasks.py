"""
List Celery tasks management command.
"""

from celery import current_app
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """List Celery tasks command"""

    help = "List Celery tasks"

    def add_arguments(self, parser):
        parser.add_argument(
            "--status",
            type=str,
            choices=["active", "scheduled"],
            help="Filter by status",
        )

    def handle(self, *args, **options):
        """Handle command execution"""
        status = options.get("status")

        inspect = current_app.control.inspect()

        if status == "active":
            tasks = inspect.active() or {}
            self.stdout.write(self.style.SUCCESS(f"Active tasks:"))
            self._display_tasks(tasks)
        elif status == "scheduled":
            tasks = inspect.scheduled() or {}
            self.stdout.write(self.style.SUCCESS(f"Scheduled tasks:"))
            self._display_scheduled_tasks(tasks)
        else:
            # List both active and scheduled
            active = inspect.active() or {}
            scheduled = inspect.scheduled() or {}

            self.stdout.write(self.style.SUCCESS(f"Active tasks:"))
            self._display_tasks(active)

            self.stdout.write(self.style.SUCCESS(f"\nScheduled tasks:"))
            self._display_scheduled_tasks(scheduled)

    def _display_tasks(self, tasks):
        """Display active tasks"""
        if not tasks:
            self.stdout.write("  No active tasks found")
            return

        for worker, task_list in tasks.items():
            self.stdout.write(f"  Worker: {worker}")
            for task in task_list:
                self.stdout.write(
                    f"    - {task.get('name', 'Unknown')} (ID: {task.get('id', 'Unknown')})"
                )

    def _display_scheduled_tasks(self, tasks):
        """Display scheduled tasks"""
        if not tasks:
            self.stdout.write("  No scheduled tasks found")
            return

        for worker, task_list in tasks.items():
            self.stdout.write(f"  Worker: {worker}")
            for task in task_list:
                request = task.get("request", {})
                task_name = request.get("name", "Unknown")
                task_id = request.get("id", "Unknown")
                eta = request.get("eta", "Unknown")
                self.stdout.write(f"    - {task_name} (ID: {task_id}, ETA: {eta})")
