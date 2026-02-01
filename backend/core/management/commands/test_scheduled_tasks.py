"""
Management command to test scheduled tasks.
"""
from background_task.models import Task
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Test and display scheduled background tasks"

    def handle(self, *args, **options):
        self.stdout.write("📋 Testing Scheduled Background Tasks")
        self.stdout.write("=" * 50)

        # Show all scheduled tasks
        tasks = Task.objects.all().order_by("run_at")

        if not tasks:
            self.stdout.write("❌ No scheduled tasks found")
            return

        self.stdout.write(f"📊 Total scheduled tasks: {tasks.count()}")
        self.stdout.write()

        for task in tasks:
            status = (
                "🟢 Pending"
                if task.attempts == 0 and not task.failed_at
                else "🔴 Failed"
                if task.failed_at
                else "🟡 Running"
            )

            self.stdout.write(f"📌 {task.task_name}")
            self.stdout.write(f"   Status: {status}")
            self.stdout.write(f"   Queue: {task.queue}")
            self.stdout.write(f"   Next Run: {task.run_at}")
            self.stdout.write(f"   Attempts: {task.attempts}")

            if task.failed_at:
                self.stdout.write(f"   Last Error: {task.last_error}")

            self.stdout.write()

        # Test one task immediately
        self.stdout.write("🧪 Testing cache warmup task...")
        try:
            from core.background_tasks import warmup_cache

            # Schedule immediate test
            test_task = warmup_cache(queue="test")
            self.stdout.write(f"✅ Test task scheduled: {test_task.id}")

        except Exception as e:
            self.stdout.write(f"❌ Failed to test task: {e}")

        self.stdout.write()
        self.stdout.write("✅ Scheduled tasks test completed!")
