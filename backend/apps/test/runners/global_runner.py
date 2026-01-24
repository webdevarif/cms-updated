"""
Global test runner.
"""
from ..services import TestRunnerService


class GlobalTestRunner:
    """Global test runner for all apps"""
    
    def __init__(self, store=None, initiated_by=None):
        self.store = store
        self.initiated_by = initiated_by
    
    def run_all_tests(self):
        """Run all tests across all apps"""
        from ..models import TestRun
        
        test_run = TestRunnerService.create_test_run(
            run_type='full',
            store=self.store,
            initiated_by=self.initiated_by
        )
        
        # Run tests for all apps
        # This would integrate with pytest to run all tests
        # For now, simulate test execution
        
        # Aggregate results
        TestRunnerService.aggregate_results(test_run)
        
        # Alert on failures
        TestRunnerService.alert_on_failure(test_run)
        
        return test_run
    
    def run_specific_tests(self, test_spec, role=None):
        """Run specific tests"""
        from ..models import TestRun
        
        test_run = TestRunnerService.create_test_run(
            run_type='custom',
            store=self.store,
            initiated_by=self.initiated_by
        )
        
        # Run specific tests
        # This would integrate with pytest to run specific tests
        # For now, simulate test execution
        
        # Aggregate results
        TestRunnerService.aggregate_results(test_run)
        
        # Alert on failures
        TestRunnerService.alert_on_failure(test_run)
        
        return test_run
    
    def run_app_tests(self, app_name, role=None):
        """Run tests for a specific app"""
        from ..models import TestRun
        
        test_run = TestRunnerService.create_test_run(
            run_type='custom',
            store=self.store,
            initiated_by=self.initiated_by
        )
        
        # Run tests for the specific app
        # This would integrate with pytest to run app-specific tests
        # For now, simulate test execution
        
        # Aggregate results
        TestRunnerService.aggregate_results(test_run)
        
        # Alert on failures
        TestRunnerService.alert_on_failure(test_run)
        
        return test_run
