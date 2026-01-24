"""
Test models.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class TestRun(models.Model):
    """
    Stores test run history and results
    """
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, null=True, blank=True)
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Run metadata
    run_type = models.CharField(max_length=50, choices=[
        ('full', 'Full Test Suite'),
        ('smoke', 'Smoke Tests'),
        ('regression', 'Regression Tests'),
        ('custom', 'Custom Test Suite')
    ], default='full')
    
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
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Error tracking
    error_message = models.TextField(blank=True)
    error_traceback = models.TextField(blank=True)
    
    class Meta:
        db_table = 'test_testrun'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"TestRun #{self.id} - {self.run_type}"
    
    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        
        if not is_new:
            old_instance = TestRun.objects.get(pk=self.pk)
            old_status = old_instance.status
        
        super().save(*args, **kwargs)
        
        from apps.logs.tasks import log_event_async
        
        if is_new:
            log_event_async.delay({
                'event_type': 'create_testrun_test',
                'message': f"Test run created: {self.run_type}",
                'store_id': self.store.id if self.store else None,
                'user_id': self.initiated_by.id if self.initiated_by else None,
                'object_id': self.id,
                'metadata': {
                    'run_type': self.run_type,
                    'total_tests': self.total_tests,
                    'status': self.status
                }
            })
        elif old_status != self.status:
            log_event_async.delay({
                'event_type': 'update_testrun_test',
                'message': f"Test run status changed: #{self.id} from {old_status} to {self.status}",
                'store_id': self.store.id if self.store else None,
                'user_id': self.initiated_by.id if self.initiated_by else None,
                'object_id': self.id,
                'metadata': {
                    'run_type': self.run_type,
                    'old_status': old_status,
                    'new_status': self.status,
                    'total_tests': self.total_tests,
                    'passed_tests': self.passed_tests,
                    'failed_tests': self.failed_tests,
                    'success_rate': self.success_rate
                }
            })


class TestResult(models.Model):
    """
    Individual test result
    """
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, null=True, blank=True)
    test_run = models.ForeignKey(TestRun, on_delete=models.CASCADE, related_name='results')

    # Test identification
    app_name = models.CharField(max_length=100)
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    role = models.CharField(max_length=50)

    # Test status
    STATUS_CHOICES = [
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
        ('error', 'Error')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='passed')

    # Timing
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    # Error details
    error_message = models.TextField(blank=True)
    error_traceback = models.TextField(blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'test_testresult'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.app_name} - {self.endpoint} ({self.role}) - {self.status}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            from apps.logs.tasks import log_event_async
            log_event_async.delay({
                'event_type': 'create_testresult_test',
                'message': f"Test result created: {self.app_name} - {self.endpoint}",
                'store_id': self.store.id if self.store else None,
                'object_id': self.id,
                'metadata': {
                    'app_name': self.app_name,
                    'endpoint': self.endpoint,
                    'method': self.method,
                    'role': self.role,
                    'status': self.status,
                    'duration_ms': self.duration_ms
                }
            })
