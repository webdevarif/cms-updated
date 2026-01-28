#!/usr/bin/env python
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")
django.setup()

from apps.test.models import TestResult, TestRun

# Check existing test runs
print("=== Existing Test Runs ===")
test_runs = TestRun.objects.all()
for tr in test_runs:
    print(
        f"TestRun #{tr.id}: status={tr.status}, progress={tr.progress_percentage}%, results={tr.results.count()}"
    )
    if tr.results.exists():
        latest = tr.results.order_by("-created_at").first()
        print(f"  Latest result: {latest.app_name}")

print("\n=== Creating Test TestRun ===")
# Create a test run
test_run = TestRun.objects.create(
    run_type="full", total_tests=0, passed_tests=0, failed_tests=0, status="running"
)

print(f"Created TestRun #{test_run.id}")
print(f"Initial progress: {test_run.progress_percentage}%")
print(f"Current app: {test_run.current_app_testing}")

# Add some test results
apps = ["accounts", "ecommerce", "entities"]
for i, app in enumerate(apps):
    TestResult.objects.create(
        test_run=test_run,
        app_name=app,
        endpoint="test_suite",
        method="TEST",
        role="system",
        status="passed",
        duration_ms=100,
    )
    print(f"Added result for {app}: progress={test_run.progress_percentage}%")

print(f"\nFinal progress: {test_run.progress_percentage}%")
print(f"Current app: {test_run.current_app_testing}")
