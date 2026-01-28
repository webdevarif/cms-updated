"""
List queue tasks management command.
"""
from apps.queue.services import QueueService
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "List queue tasks"

    def add_arguments(self, parser):
        parser.add_argument(
            "--status", type=str, choices=["active", "scheduled", "failed"], help="Filter by status"
        )

    def handle(self, *args, **options):
        status = options.get("status")

        if status == "active":
            tasks = QueueService.get_active_tasks()
            self.stdout.write(self.style.SUCCESS(f"Active tasks ({len(tasks)}):"))
            for task in tasks:
                self.stdout.write(
                    f"  - {task['task_id']}: {task['name']} (worker: {task['worker']})"
                )

        elif status == "scheduled":
            tasks = QueueService.get_scheduled_tasks()
            self.stdout.write(self.style.SUCCESS(f"Scheduled tasks ({len(tasks)}):"))
            for task in tasks:
                self.stdout.write(f"  - {task['task_id']}: {task['name']} (ETA: {task['eta']})")

        else:
            # List both active and scheduled
            active = QueueService.get_active_tasks()
            scheduled = QueueService.get_scheduled_tasks()

            self.stdout.write(self.style.SUCCESS(f"Active tasks ({len(active)}):"))
            for task in active:
                self.stdout.write(
                    f"  - {task['task_id']}: {task['name']} (worker: {task['worker']})"
                )

            self.stdout.write(self.style.SUCCESS(f"\nScheduled tasks ({len(scheduled)}):"))
            for task in scheduled:
                self.stdout.write(f"  - {task['task_id']}: {task['name']} (ETA: {task['eta']})")
