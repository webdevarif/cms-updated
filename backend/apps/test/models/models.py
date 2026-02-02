"""
Test models.
"""

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class TestRun(models.Model):
    """
    Stores test run history and results
    """

    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, null=True, blank=True)
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Run metadata
    run_type = models.CharField(
        max_length=50,
        choices=[
            ("full", "Full Test Suite"),
            ("smoke", "Smoke Tests"),
            ("regression", "Regression Tests"),
            ("custom", "Custom Test Suite"),
        ],
        default="full",
    )

    # Results
    total_tests = models.PositiveIntegerField(default=0)
    passed_tests = models.PositiveIntegerField(default=0)
    failed_tests = models.PositiveIntegerField(default=0)
    skipped_tests = models.PositiveIntegerField(default=0)

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)

    # Report
    html_report = models.TextField(blank=True)
    report_path = models.CharField(max_length=255, blank=True)

    # Status
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Error tracking
    error_message = models.TextField(blank=True)
    error_traceback = models.TextField(blank=True)

    class Meta:
        db_table = "test_testrun"
        ordering = ["-started_at"]

    def __str__(self):
        return f"TestRun #{self.id} - {self.run_type}"

    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100

    @property
    def progress_percentage(self):
        """Calculate progress percentage based on test results"""
        if self.status == "completed":
            return 100
        elif self.status == "failed":
            return 0
        elif self.status == "pending":
            return 0
        else:
            # Calculate based on completed test results
            try:
                completed_apps = self.results.count()
                total_apps = 16  # Total apps in our system

                if completed_apps == 0:
                    # If no results yet but status is running, show minimal progress
                    return 1  # Show at least 1% to indicate it's started

                return int((completed_apps / total_apps) * 100)
            except Exception:
                # Fallback calculation based on total_tests if available
                if self.total_tests > 0:
                    # Estimate progress based on total_tests (rough estimate: ~6 tests per app)
                    estimated_apps_completed = min(self.total_tests // 6, 16)
                    return int((estimated_apps_completed / 16) * 100)
                return 0

    @property
    def current_app_testing(self):
        """Get the current app being tested"""
        if self.status in ["completed", "failed", "pending"]:
            return None

        try:
            apps_to_test = [
                "accounts",
                "ecommerce",
                "entities",
                "forms",
                "giftcards",
                "logs",
                "mediafile",
                "metafields",
                "notifications",
                "pages",
                "posts",
                "search",
                "stores",
                "test",
                "themes",
                "webhooks",
            ]

            completed_apps = self.results.count()
            if completed_apps < len(apps_to_test):
                return apps_to_test[completed_apps]  # Current app being tested
            else:
                # All apps completed, return the last one
                latest_result = self.results.order_by("-created_at").first()
                if latest_result:
                    return latest_result.app_name
        except Exception:
            pass

        return "Unknown"

    @property
    def estimated_remaining_time(self):
        """Estimate remaining time in seconds"""
        from django.utils import timezone

        if self.status == "completed":
            return 0
        elif self.status == "failed":
            return 0
        elif self.status == "pending":
            return 60  # Estimate 1 minute for full suite
        elif self.progress_percentage == 0:
            return 60
        else:
            # Estimate based on elapsed time and progress
            if self.started_at:
                elapsed = (timezone.now() - self.started_at).total_seconds()
                if self.progress_percentage > 0:
                    estimated_total = elapsed / (self.progress_percentage / 100)
                    return max(0, int(estimated_total - elapsed))
            return 30

    def start_background_test(self, run_type="full", app_name=None):
        """Start this test run in the background using django-background-tasks
        with fallback to threading"""
        import logging

        logger = logging.getLogger(__name__)

        if self.status == "pending":
            logger.info(f"Starting background test for TestRun #{self.id}, type: {run_type}")
            self.status = "running"
            self.save()

            # Use Celery tasks for background execution
            try:
                # Import Celery tasks
                from core.background_tasks import run_app_tests, run_full_test_suite

                # Schedule the test execution
                if run_type == "app" and app_name:
                    # Run specific app tests
                    task = run_app_tests.delay(app_name)
                    logger.info(
                        f"Scheduled app test execution for TestRun #{self.id}, task_id: {task.id}"
                    )
                else:
                    # Run full test suite
                    task = run_full_test_suite.delay()
                    logger.info(
                        f"Scheduled full test suite execution for TestRun #{self.id}, "
                        f"task_id: {task.id}"
                    )

                return task

            except Exception as e:
                # Fallback to threading if Celery tasks fails
                logger.warning(
                    f"Celery tasks failed, falling back to threading for TestRun #{self.id}: {e}"
                    f"django-background-tasks failed, falling back to threading "
                    f"for TestRun #{self.id}: {e}"
                )

                # Use the simple threading fallback
                from core.background_tasks import BackgroundTestRunner

                thread = BackgroundTestRunner.start_background_test(
                    self.id, run_type=run_type, app_name=app_name
                )
                logger.info(f"Started background test thread for TestRun #{self.id}")
                return thread
        else:
            logger.warning(
                f"Cannot start background test for TestRun #{self.id}: " f"status is {self.status}"
            )
            return None

    def stop_background_test(self):
        """Stop this test run"""
        # Mark as cancelled - Celery tasks can't be easily stopped once started
        self.status = "cancelled"
        self.save()
        return True

    def is_background_test_running(self):
        """Check if this test is running in background"""
        return self.status == "running"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None

        if not is_new:
            old_instance = TestRun.objects.get(pk=self.pk)
            old_status = old_instance.status

        super().save(*args, **kwargs)

        # Try to send event, but handle gracefully if event service is not available
        try:
            from apps.analytics.services.event_service import EventService

            if is_new:
                EventService.log_event(
                    event_type="create_testrun_test",
                    event_name=f"Test run created: {self.run_type}",
                    properties={
                        "run_type": self.run_type,
                        "testrun_id": self.id,
                    },
                    store=self.store,
                )
            elif old_status != self.status:
                EventService.log_event(
                    event_type="update_testrun_test",
                    event_name=f"Test run status changed: {old_status} -> {self.status}",
                    properties={
                        "old_status": old_status,
                        "new_status": self.status,
                        "testrun_id": self.id,
                    },
                    store=self.store,
                )
        except Exception as e:
            # Log the error but don't fail the save operation
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"Could not send event for TestRun: {e}")


class TestResult(models.Model):
    """
    Individual test result
    """

    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, null=True, blank=True)
    test_run = models.ForeignKey(TestRun, on_delete=models.CASCADE, related_name="results")

    # Test identification
    app_name = models.CharField(max_length=100)
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    role = models.CharField(max_length=50)

    # Test status
    STATUS_CHOICES = [
        ("passed", "Passed"),
        ("failed", "Failed"),
        ("skipped", "Skipped"),
        ("error", "Error"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="passed")

    # Timing
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    # Error details
    error_message = models.TextField(blank=True)
    error_traceback = models.TextField(blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "test_testresult"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.app_name} - {self.endpoint} ({self.role}) - {self.status}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Try to send event, but handle gracefully if event service is not available
        try:
            from apps.analytics.services.event_service import EventService

            if is_new:
                EventService.log_event(
                    event_type="create_testresult_test",
                    event_name=f"Test result created: {self.app_name} - {self.endpoint}",
                    properties={
                        "app_name": self.app_name,
                        "endpoint": self.endpoint,
                        "status": self.status,
                        "testresult_id": self.id,
                    },
                    store=self.test_run.store,
                )
        except Exception as e:
            # Log the error but don't fail the save operation
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"Could not send event for TestResult: {e}")
