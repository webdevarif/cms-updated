"""
Admin configuration for test module.
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import TestResult, TestRun


@admin.register(TestRun)
class TestRunAdmin(admin.ModelAdmin):
    """Admin for TestRun - Simplified and user-friendly"""

    # Simplified list display with only essential fields
    list_display = [
        "id",
        "run_type_display",
        "status_badge",
        "progress_summary",
        "results_summary",
        "started_at",
    ]
    list_filter = ["status", "run_type", "started_at"]
    search_fields = ["run_type", "status"]
    readonly_fields = ["started_at", "completed_at", "duration_seconds"]
    date_hierarchy = "started_at"
    actions = ["start_background_tests", "stop_background_tests"]

    # Custom field configurations
    fieldsets = (
        ("Test Information", {"fields": ("run_type", "status", "initiated_by")}),
        (
            "Results Summary",
            {
                "fields": (
                    "total_tests",
                    "passed_tests",
                    "failed_tests",
                    "success_rate_display",
                )
            },
        ),
        (
            "Timing",
            {
                "fields": ("started_at", "completed_at", "duration_seconds"),
                "classes": ("collapse",),
            },
        ),
        ("Reports", {"fields": ("report_link",), "classes": ("collapse",)}),
        (
            "Error Details",
            {
                "fields": ("error_message", "error_traceback"),
                "classes": ("collapse",),
                "description": "Only shown when tests fail",
            },
        ),
    )

    def run_type_display(self, obj):
        """Display run type with emoji"""
        icons = {"full": "🔬", "smoke": "💨", "regression": "🔄", "custom": "⚙️"}
        return format_html("{} {}", icons.get(obj.run_type, "📋"), obj.get_run_type_display())

    run_type_display.short_description = "Type"

    def status_badge(self, obj):
        """Display status as a colored badge"""
        colors = {
            "pending": "#6c757d",
            "running": "#007bff",
            "completed": "#28a745",
            "failed": "#dc3545",
            "cancelled": "#ffc107",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display().upper(),
        )

    status_badge.short_description = "Status"

    def progress_summary(self, obj):
        """Compact progress display"""
        if obj.status == "completed":
            return format_html("✅ <strong>100%</strong>")
        elif obj.status == "failed":
            return format_html("❌ <strong>Failed</strong>")
        elif obj.status == "cancelled":
            return format_html("⏹️ <strong>Cancelled</strong>")
        elif obj.status == "running":
            percentage = obj.progress_percentage
            current_app = obj.current_app_testing or "Unknown"

            # Simple progress indicator
            if percentage < 25:
                bar = "🔴"
            elif percentage < 50:
                bar = "🟡"
            elif percentage < 75:
                bar = "🟠"
            else:
                bar = "🟢"

            return format_html(
                "{} {}%<br><small>Testing: {}</small>",
                bar,
                percentage,
                current_app[:15] + "..." if len(current_app) > 15 else current_app,
            )
        else:
            return format_html("⏳ <strong>Pending</strong>")

    progress_summary.short_description = "Progress"

    def results_summary(self, obj):
        """Compact results display"""
        if obj.total_tests == 0:
            return "No tests run"

        passed = obj.passed_tests
        failed = obj.failed_tests
        total = obj.total_tests

        if failed == 0:
            return format_html("✅ <strong>{}/{}</strong>", passed, total)
        elif passed == 0:
            return format_html("❌ <strong>{}/{}</strong>", failed, total)
        else:
            return format_html("✅ {} ❌ {}<br><small>Total: {}</small>", passed, failed, total)

    results_summary.short_description = "Results"

    def success_rate_display(self, obj):
        """Display success rate as a percentage"""
        rate = obj.success_rate
        if rate >= 90:
            color = "#28a745"
        elif rate >= 70:
            color = "#ffc107"
        else:
            color = "#dc3545"

        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>', color, rate
        )

    success_rate_display.short_description = "Success Rate"

    def report_link(self, obj):
        """Link to detailed report"""
        if obj.html_report:
            report_url = reverse("admin:test_testrun_change", args=[obj.id])
            return format_html('<a href="{}" class="button">View Full Report</a>', report_url)
        return "No report available"

    report_link.short_description = "Full Report"

    def get_readonly_fields(self, request, obj=None):
        """Make fields readonly based on object state"""
        readonly = list(self.readonly_fields)
        if obj and obj.status not in ["pending", "running"]:
            readonly.extend(["run_type", "status"])
        return readonly

    # Actions
    def start_background_tests(self, request, queryset):
        """Start selected test runs in background"""
        started_count = 0
        for test_run in queryset:
            if test_run.status == "pending":
                test_run.start_background_test()
                started_count += 1

        self.message_user(request, f"✅ Started {started_count} test runs in background.")

    start_background_tests.short_description = "🚀 Start tests"

    def stop_background_tests(self, request, queryset):
        """Stop selected test runs"""
        stopped_count = 0
        for test_run in queryset:
            if test_run.stop_background_test():
                stopped_count += 1

        self.message_user(request, f"⏹️ Stopped {stopped_count} test runs.")

    stop_background_tests.short_description = "⏹️ Stop tests"

    # Custom admin site settings
    change_list_template = "admin/test/testrun_change_list.html"
    change_form_template = "admin/test/testrun_change_form.html"

    def changelist_view(self, request, extra_context=None):
        """Add custom context variables for the dashboard"""
        response = super().changelist_view(request, extra_context)

        # Calculate stats
        queryset = self.get_queryset(request)
        completed_count = queryset.filter(status="completed").count()
        failed_count = queryset.filter(status="failed").count()
        running_count = queryset.filter(status="running").count()
        has_running_tests = running_count > 0

        # Add to context
        response.context_data["completed_count"] = completed_count
        response.context_data["failed_count"] = failed_count
        response.context_data["running_count"] = running_count
        response.context_data["has_running_tests"] = has_running_tests

        return response


class TestResultInline(admin.TabularInline):
    """Inline test results for TestRun"""

    model = TestResult
    extra = 0
    fields = ["app_name_badge", "endpoint_summary", "status_badge", "duration_display"]
    readonly_fields = [
        "app_name_badge",
        "endpoint_summary",
        "status_badge",
        "duration_display",
    ]
    can_delete = False
    max_num = 10  # Limit to 10 results for performance

    def app_name_badge(self, obj):
        """Display app name as a badge"""
        colors = {
            "accounts": "#007bff",
            "ecommerce": "#28a745",
            "entities": "#17a2b8",
            "forms": "#ffc107",
            "search": "#6f42c1",
            "stores": "#e83e8c",
        }
        color = colors.get(obj.app_name, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px;">{}</span>',
            color,
            obj.app_name.upper(),
        )

    app_name_badge.short_description = "App"

    def endpoint_summary(self, obj):
        """Show truncated endpoint"""
        endpoint = obj.endpoint
        if len(endpoint) > 30:
            endpoint = endpoint[:27] + "..."
        return format_html(
            "<strong>{}</strong><br><small>{} {}</small>",
            endpoint,
            obj.method,
            obj.role,
        )

    endpoint_summary.short_description = "Endpoint"

    def status_badge(self, obj):
        """Display status as a small badge"""
        colors = {
            "passed": "#28a745",
            "failed": "#dc3545",
            "skipped": "#ffc107",
            "error": "#fd7e14",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display().upper(),
        )

    status_badge.short_description = "Status"

    def duration_display(self, obj):
        """Display duration in a readable format"""
        if obj.duration_ms:
            if obj.duration_ms < 1000:
                return f"{obj.duration_ms}ms"
            else:
                return f"{obj.duration_ms/1000:.1f}s"
        return "-"

    duration_display.short_description = "Duration"


# Add the inline to TestRunAdmin
TestRunAdmin.inlines = [TestResultInline]


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    """Admin for TestResult - Simplified for detailed viewing"""

    list_display = [
        "test_run_link",
        "app_name_badge",
        "endpoint_summary",
        "status_badge",
        "duration_display",
        "error_summary",
    ]
    list_filter = ["status", "app_name", "role", "created_at"]
    search_fields = ["app_name", "endpoint", "error_message"]
    readonly_fields = [
        "created_at",
        "test_run",
        "app_name",
        "endpoint",
        "method",
        "role",
        "duration_ms",
    ]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Test Information",
            {"fields": ("test_run", "app_name", "endpoint", "method", "role")},
        ),
        ("Results", {"fields": ("status_badge", "duration_display", "created_at")}),
        (
            "Error Details",
            {
                "fields": ("error_message", "error_traceback"),
                "classes": ("collapse",),
                "description": "Error information (only shown when test fails)",
            },
        ),
        ("Metadata", {"fields": ("metadata",), "classes": ("collapse",)}),
    )

    def test_run_link(self, obj):
        """Link to the test run"""
        url = reverse("admin:test_testrun_change", args=[obj.test_run.id])
        return format_html('<a href="{}">Test Run #{}</a>', url, obj.test_run.id)

    test_run_link.short_description = "Test Run"

    def app_name_badge(self, obj):
        """Display app name as a badge"""
        colors = {
            "accounts": "#007bff",
            "ecommerce": "#28a745",
            "entities": "#17a2b8",
            "forms": "#ffc107",
            "search": "#6f42c1",
            "stores": "#e83e8c",
        }
        color = colors.get(obj.app_name, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px;">{}</span>',
            color,
            obj.app_name.upper(),
        )

    app_name_badge.short_description = "App"

    def endpoint_summary(self, obj):
        """Show endpoint with method and role"""
        return format_html(
            "<strong>{}</strong><br><small>{} • {}</small>",
            obj.endpoint,
            obj.method,
            obj.role,
        )

    endpoint_summary.short_description = "Endpoint"

    def status_badge(self, obj):
        """Display status as a badge"""
        colors = {
            "passed": "#28a745",
            "failed": "#dc3545",
            "skipped": "#ffc107",
            "error": "#fd7e14",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display().upper(),
        )

    status_badge.short_description = "Status"

    def duration_display(self, obj):
        """Display duration in a readable format"""
        if obj.duration_ms:
            if obj.duration_ms < 1000:
                return format_html(
                    '<span style="color: #28a745;">{}</span>', f"{obj.duration_ms}ms"
                )
            elif obj.duration_ms < 5000:
                return format_html(
                    '<span style="color: #ffc107;">{}</span>',
                    f"{obj.duration_ms/1000:.1f}s",
                )
            else:
                return format_html(
                    '<span style="color: #dc3545;">{}</span>',
                    f"{obj.duration_ms/1000:.1f}s",
                )
        return "-"

    duration_display.short_description = "Duration"

    def error_summary(self, obj):
        """Show error summary"""
        if obj.status in ["failed", "error"] and obj.error_message:
            error = obj.error_message
            if len(error) > 50:
                error = error[:47] + "..."
            return format_html(
                '<span style="color: #dc3545;" title="{}">⚠️ {}</span>',
                obj.error_message,
                error,
            )
        return ""

    error_summary.short_description = "Error"

    def has_add_permission(self, request):
        """Disable manual addition of test results"""
        return False

    def has_change_permission(self, request, obj=None):
        """Test results should not be editable"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deletion of test results"""
        return request.user.is_superuser
