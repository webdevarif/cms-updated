"""
Admin configuration for test module.
"""
from django.contrib import admin
from .models import TestRun, TestResult


@admin.register(TestRun)
class TestRunAdmin(admin.ModelAdmin):
    """Admin for TestRun"""
    list_display = ['id', 'run_type', 'status', 'total_tests', 'passed_tests', 'failed_tests', 'success_rate', 'started_at']
    list_filter = ['status', 'run_type']
    readonly_fields = ['started_at', 'completed_at', 'duration_seconds']
    date_hierarchy = 'started_at'


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    """Admin for TestResult"""
    list_display = ['test_run', 'app_name', 'endpoint', 'method', 'role', 'status', 'duration_ms']
    list_filter = ['status', 'app_name', 'role']
    readonly_fields = ['created_at']
