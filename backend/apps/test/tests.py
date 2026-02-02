"""
Basic Django tests for the test app.
"""

from apps.test.models import TestResult, TestRun
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class TestRunModelTest(TestCase):
    """Test the TestRun model"""

    def test_create_test_run(self):
        """Test creating a test run"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        test_run = TestRun.objects.create(
            run_type="full",
            initiated_by=user,
            total_tests=10,
            passed_tests=8,
            failed_tests=2,
            status="completed",
        )

        self.assertEqual(test_run.run_type, "full")
        self.assertEqual(test_run.initiated_by, user)
        self.assertEqual(test_run.total_tests, 10)
        self.assertEqual(test_run.success_rate, 80.0)
        self.assertEqual(str(test_run), f"TestRun #{test_run.id} - full")

    def test_testrun_success_rate_calculation(self):
        """Test success rate calculation"""
        test_run = TestRun(total_tests=0)
        self.assertEqual(test_run.success_rate, 0.0)

        test_run.total_tests = 10
        test_run.passed_tests = 5
        self.assertEqual(test_run.success_rate, 50.0)


class TestResultModelTest(TestCase):
    """Test the TestResult model"""

    def test_create_test_result(self):
        """Test creating a test result"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        test_run = TestRun.objects.create(run_type="custom", initiated_by=user, status="completed")

        test_result = TestResult.objects.create(
            test_run=test_run,
            app_name="test_app",
            endpoint="test_endpoint",
            method="GET",
            role="public",
            status="passed",
            duration_ms=150,
        )

        self.assertEqual(test_result.test_run, test_run)
        self.assertEqual(test_result.app_name, "test_app")
        self.assertEqual(test_result.status, "passed")
        self.assertEqual(str(test_result), "test_app - test_endpoint (GET) - passed")
