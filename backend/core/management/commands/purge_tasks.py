"""
Purge Celery tasks management command.
"""

from celery import current_app
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Purge Celery tasks command"""

    help = "Purge Celery tasks"

    def add_arguments(self, parser):
        parser.add_argument("--queue", type=str, help="Purge tasks by queue name")
        parser.add_argument("--force", action="store_true", help="Force purge without confirmation")

    def handle(self, *args, **options):
        """Handle command execution"""
        queue = options.get("queue")
        force = options.get("force")

        if not force:
            if queue:
                confirm = input(
                    f"Are you sure you want to purge all tasks in queue '{queue}'? (y/N): "
                )
            else:
                confirm = input(
                    "Are you sure you want to purge ALL tasks? This action cannot be undone! (y/N): "
                )

            if confirm.lower() not in ["y", "yes"]:
                self.stdout.write("Purge cancelled.")
                return

        try:
            if queue:
                # Purge tasks by queue
                purged_count = current_app.control.purge(destination=[queue])
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully purged {purged_count} tasks from queue '{queue}'"
                    )
                )
            else:
                # Purge all tasks
                purged_count = current_app.control.purge()
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully purged {purged_count} tasks from all queues")
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error purging tasks: {str(e)}"))
