"""
Admin configuration for test module.
"""
from django.contrib import admin
from django.utils.html import format_html

from .models import TestResult, TestRun


@admin.register(TestRun)
class TestRunAdmin(admin.ModelAdmin):
    """Admin for TestRun"""

    list_display = [
        "id",
        "run_type",
        "status",
        "progress_display",
        "current_app_testing",
        "total_tests",
        "passed_tests",
        "failed_tests",
        "success_rate",
        "started_at",
    ]
    list_filter = ["status", "run_type"]
    readonly_fields = ["started_at", "completed_at", "duration_seconds", "progress_percentage"]
    date_hierarchy = "started_at"
    actions = ["start_background_tests", "stop_background_tests"]

    # Make progress_display non-sortable
    def get_ordering(self, request):
        return ["-started_at"]  # Only sort by start date, not by progress

    def progress_display(self, obj):
        """Display progress as a percentage bar"""
        if obj.status == "completed":
            return format_html("✅ <strong>100% Complete</strong>")
        elif obj.status == "failed":
            return format_html("❌ <strong>Failed</strong>")
        elif obj.status == "cancelled":
            return format_html("⏹️ <strong>Cancelled</strong>")
        elif obj.status == "running":
            percentage = obj.progress_percentage
            remaining = obj.estimated_remaining_time
            current_app = obj.current_app_testing or "Unknown"

            # Create a simple progress bar
            bar_length = 20
            filled_length = int(bar_length * percentage / 100)
            bar = "█" * filled_length + "░" * (bar_length - filled_length)

            return format_html(
                "🔄 {}% <code>[{}]</code><br><small>Testing: {}<br>~{}s remaining</small>",
                percentage,
                bar,
                current_app,
                remaining,
            )
        else:
            return format_html("⏳ <strong>Pending</strong>")

    progress_display.short_description = "Progress"
    progress_display.allow_tags = True
    progress_display.admin_order_field = None  # Make non-sortable

    def start_background_tests(self, request, queryset):
        """Start selected test runs in background"""
        started_count = 0
        for test_run in queryset:
            if test_run.status == "pending":
                test_run.start_background_test()
                started_count += 1

        self.message_user(request, f"Started {started_count} test runs in background.")

    start_background_tests.short_description = "Start background tests"

    def stop_background_tests(self, request, queryset):
        """Stop selected test runs"""
        stopped_count = 0
        for test_run in queryset:
            if test_run.stop_background_test():
                stopped_count += 1

        self.message_user(request, f"Stopped {stopped_count} test runs.")

    stop_background_tests.short_description = "Stop background tests"


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    """Admin for TestResult"""

    list_display = ["test_run", "app_name", "endpoint", "method", "role", "status", "duration_ms"]
    list_filter = ["status", "app_name", "role"]
    readonly_fields = ["created_at"]
