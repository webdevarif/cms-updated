"""
Services for test module.
"""
from django.db import transaction
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class TestRunnerService:
    """Global test runner service"""
    
    @staticmethod
    @transaction.atomic
    def create_test_run(run_type='full', store=None, initiated_by=None):
        """Create a new test run"""
        from .models import TestRun
        
        from core.services.store import StoreService
        
        test_run = TestRun.objects.create(
            store=StoreService.create_store(name='Test Store', slug='test-store'),
            initiated_by=initiated_by,
            run_type=run_type,
            status='running'
        )
        
        logger.info(f"Created TestRun #{test_run.id} - {run_type}")
        return test_run
    
    @staticmethod
    def record_result(test_run, app_name, endpoint, method, role, status, duration_ms=None, error_message=None, error_traceback=None, metadata=None):
        """Record an individual test result"""
        from .models import TestResult
        
        return TestResult.objects.create(
            test_run=test_run,
            app_name=app_name,
            endpoint=endpoint,
            method=method,
            role=role,
            status=status,
            duration_ms=duration_ms,
            error_message=error_message,
            error_traceback=error_traceback,
            metadata=metadata or {}
        )
    
    @staticmethod
    def aggregate_results(test_run):
        """Aggregate test results for a test run"""
        from .models import TestResult
        
        results = TestResult.objects.filter(test_run=test_run)
        
        total = results.count()
        passed = results.filter(status='passed').count()
        failed = results.filter(status='failed').count()
        skipped = results.filter(status='skipped').count()
        errors = results.filter(status='error').count()
        
        # Update test run
        test_run.total_tests = total
        test_run.passed_tests = passed
        test_run.failed_tests = failed
        test_run.skipped_tests = skipped
        test_run.status = 'completed'
        test_run.completed_at = timezone.now()
        
        if test_run.started_at:
            duration = (test_run.completed_at - test_run.started_at).total_seconds()
            test_run.duration_seconds = duration
        
        test_run.save()
        
        logger.info(f"TestRun #{test_run.id} completed - {passed}/{total} passed ({test_run.success_rate:.1f}%)")
        
        return test_run
    
    @staticmethod
    def get_test_history(store=None, limit=10):
        """Get recent test run history"""
        queryset = TestRun.objects.all()
        
        if store:
            queryset = queryset.filter(store=store)
        
        return queryset.order_by('-started_at')[:limit]
    
    @staticmethod
    def get_test_stats(store=None, days=30):
        """Get test statistics"""
        from django.utils import timezone
        from datetime import timedelta
        
        since = timezone.now() - timedelta(days=days)
        
        queryset = TestRun.objects.filter(
            started_at__gte=since
        )
        
        if store:
            queryset = queryset.filter(store=store)
        
        total = queryset.count()
        completed = queryset.filter(status='completed').count()
        
        total_tests = queryset.aggregate(total=models.Sum('total_tests'))['total'] or 0
        passed_tests = queryset.aggregate(passed=models.Sum('passed_tests'))['passed'] or 0
        
        return {
            'total_runs': total,
            'completed_runs': completed,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
    
    @staticmethod
    def alert_on_failure(test_run):
        """Send email alert on test failures"""
        if test_run.failed_tests > 0:
            from apps.smtp.services import SMTPService
            from django.conf import settings
            
            # Get recipients (store owner or admin)
            recipients = []
            if test_run.store:
                recipients.append(test_run.store.owner.email)
            if test_run.initiated_by:
                recipients.append(test_run.initiated_by.email)
            
            # Send alert email
            SMTPService.send_template_email(
                template_name='test_failure_alert',
                recipients=recipients,
                subject=f'Test Failure Alert - {test_run.run_type} - {test_run.failed_tests} Failed',
                html_content=f'''
                <h2>Test Failure Alert</h2>
                <p><strong>Test Run:</strong> #{test_run.id}</p>
                <p><strong>Type:</strong> {test_run.run_type}</p>
                <p><strong>Failed Tests:</strong> {test_run.failed_tests}/{test_run.total_tests}</p>
                <p><strong>Success Rate:</strong> {test_run.success_rate:.1f}%</p>
                <p><strong>Started:</strong> {test_run.started_at}</p>
                <p><strong>Completed:</strong> {test_run.completed_at}</p>
                <hr>
                <p><a href="{settings.BASE_URL}/test/reports/{test_run.id}/">View Full Report</a></p>
                ''',
                store=test_run.store
            )
            
            logger.info(f"Test failure alert sent for TestRun #{test_run.id}")
