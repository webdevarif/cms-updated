"""
Management command to test scheduled tasks.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Test and display Celery scheduled tasks"

    def handle(self, *args, **options):
        self.stdout.write("📋 Testing Celery Scheduled Tasks")
        self.stdout.write("=" * 50)

        # Import Celery app to inspect scheduled tasks
        try:
            from core.celery import app

            # Get beat schedule
            beat_schedule = app.conf.beat_schedule

            if not beat_schedule:
                self.stdout.write("❌ No scheduled tasks found in Celery beat schedule")
                return

            self.stdout.write(f"📊 Total scheduled tasks: {len(beat_schedule)}")
            self.stdout.write()

            for task_name, task_config in beat_schedule.items():
                self.stdout.write(f"📌 {task_name}")
                self.stdout.write(f"   Task: {task_config['task']}")
                self.stdout.write(f"   Schedule: {task_config['schedule']}")
                if "options" in task_config:
                    self.stdout.write(f"   Options: {task_config['options']}")
                self.stdout.write()

            self.stdout.write()
            self.stdout.write("✅ Celery scheduled tasks test completed!")

        except Exception as e:
            self.stdout.write(f"❌ Error testing scheduled tasks: {e}")
