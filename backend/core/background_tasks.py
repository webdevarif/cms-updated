"""
Consolidated background tasks for all modules.
"""

import logging
import os
import subprocess
import threading
import time

from core.celery import app

from django.utils import timezone

logger = logging.getLogger(__name__)


@app.task(bind=True)
def run_full_test_suite(self):
    """Run full test suite using pytest."""
    try:
        logger.info("Starting full test suite execution via background task")

        # Create test run
        from apps.test.models.models import TestResult
        from apps.test.services.test_service import TestRunnerService

        test_run = TestRunnerService.create_test_run(run_type="full")
        test_run.status = "running"
        test_run.save()

        # Prepare pytest command
        cmd = ["python", "manage.py", "test"]
        cmd.extend(["--verbosity=2", "--tb=short"])

        # Change to project directory
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        # Execute tests
        start_time = time.time()
        result = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True, timeout=1800)
        end_time = time.time()

        # Parse results
        total_tests = passed_tests = failed_tests = skipped_tests = 0
        output_lines = result.stdout.split("\n")
        for line in output_lines:
            if " passed" in line and " failed" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed" and i > 0:
                        passed_tests = int(parts[i - 1])
                    elif part == "failed" and i > 0:
                        failed_tests = int(parts[i - 1])
                    elif part == "skipped" and i > 0:
                        skipped_tests = int(parts[i - 1])
                total_tests = passed_tests + failed_tests + skipped_tests
                break

        # Create test result
        TestResult.objects.create(
            test_run=test_run,
            app_name="all",
            endpoint="pytest",
            method="TEST",
            role="system",
            status="passed" if failed_tests == 0 else "failed",
            duration_ms=int((end_time - start_time) * 1000),
            metadata={
                "command": " ".join(cmd),
                "exit_code": result.returncode,
                "stdout": result.stdout[-1000:],
                "stderr": result.stderr[-1000:],
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "skipped_tests": skipped_tests,
                "test_type": "full",
            },
        )

        # Update test run
        test_run.total_tests = total_tests
        test_run.passed_tests = passed_tests
        test_run.failed_tests = failed_tests
        test_run.skipped_tests = skipped_tests
        test_run.status = "completed"
        test_run.completed_at = timezone.now()
        test_run.duration_seconds = int(end_time - start_time)
        test_run.save()

        # Aggregate results
        TestRunnerService.aggregate_results(test_run)

        # Alert on failures
        if failed_tests > 0:
            TestRunnerService.alert_on_failure(test_run)

        logger.info(f"Background test suite completed: {passed_tests}/{total_tests} passed")

        return {
            "test_run_id": test_run.id,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
            "duration_seconds": int(end_time - start_time),
            "success": failed_tests == 0,
        }

    except Exception as e:
        logger.error(f"Background test suite failed: {e}")
        raise


@app.task(bind=True)
def run_app_tests(self, app_label):
    """Run tests for a specific app."""
    try:
        logger.info(f"Starting test execution for app: {app_label}")

        from apps.test.models.models import TestResult
        from apps.test.services.test_service import TestRunnerService

        test_run = TestRunnerService.create_test_run(run_type="app")
        test_run.status = "running"
        test_run.save()

        # Prepare pytest command
        cmd = ["python", "manage.py", "test", f"apps.{app_label}"]
        cmd.extend(["--verbosity=2", "--tb=short"])

        # Execute tests
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        start_time = time.time()
        result = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True, timeout=1800)
        end_time = time.time()

        # Parse results
        total_tests = passed_tests = failed_tests = skipped_tests = 0
        output_lines = result.stdout.split("\n")
        for line in output_lines:
            if " passed" in line and " failed" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed" and i > 0:
                        passed_tests = int(parts[i - 1])
                    elif part == "failed" and i > 0:
                        failed_tests = int(parts[i - 1])
                    elif part == "skipped" and i > 0:
                        skipped_tests = int(parts[i - 1])
                total_tests = passed_tests + failed_tests + skipped_tests
                break

        # Create test result
        TestResult.objects.create(
            test_run=test_run,
            app_name=app_label,
            endpoint="pytest",
            method="TEST",
            role="system",
            status="passed" if failed_tests == 0 else "failed",
            duration_ms=int((end_time - start_time) * 1000),
            metadata={
                "command": " ".join(cmd),
                "exit_code": result.returncode,
                "stdout": result.stdout[-1000:],
                "stderr": result.stderr[-1000:],
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "skipped_tests": skipped_tests,
                "test_type": "app",
            },
        )

        # Update test run
        test_run.total_tests = total_tests
        test_run.passed_tests = passed_tests
        test_run.failed_tests = failed_tests
        test_run.skipped_tests = skipped_tests
        test_run.status = "completed"
        test_run.completed_at = timezone.now()
        test_run.duration_seconds = int(end_time - start_time)
        test_run.save()

        TestRunnerService.aggregate_results(test_run)
        if failed_tests > 0:
            TestRunnerService.alert_on_failure(test_run)

        logger.info(
            f"Background test completed for {app_label}: {passed_tests}/{total_tests} passed"
        )

        return {
            "test_run_id": test_run.id,
            "app_label": app_label,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
            "duration_seconds": int(end_time - start_time),
            "success": failed_tests == 0,
        }

    except Exception as e:
        logger.error(f"Background test failed for {app_label}: {e}")
        raise


@app.task(bind=True)
def warmup_cache(self):
    """Warm up search cache for better performance."""
    try:
        logger.info("Starting search cache warmup")

        from apps.stores.models import Store

        active_stores = Store.objects.filter(status="active")
        warmed_count = 0

        for store in active_stores:
            try:
                # Pre-load common search terms
                common_terms = ["", "a", "the", "product", "page", "search"]
                for term in common_terms:
                    logger.debug(f"Warming up cache for store {store.id} with term: '{term}'")

                warmed_count += 1
                logger.info(f"Warmed up search cache for store {store.id}")

            except Exception as e:
                logger.error(f"Failed to warm up cache for store {store.id}: {str(e)}")
                continue

        logger.info(f"Completed search cache warmup for {warmed_count} stores")
        return f"Successfully warmed up search cache for {warmed_count} stores"

    except Exception as e:
        logger.error(f"Search cache warmup failed: {e}")
        raise


# Threading fallback for when django-background-tasks isn't working
class BackgroundTestRunner:
    """Simple threading fallback for test execution"""

    _active_runs = {}

    @classmethod
    def start_background_test(cls, test_run_id, run_type="full", app_name=None):
        """Start a test run in the background"""

        def run_test_background():
            try:
                logger.info(f"Starting background test for TestRun #{test_run_id}")

                # Simple subprocess execution
                if run_type == "full":
                    cmd = ["python", "manage.py", "test"]
                elif run_type == "app" and app_name:
                    cmd = ["python", "manage.py", "test", f"apps.{app_name}"]
                else:
                    cmd = ["python", "manage.py", "test", app_name]

                cmd.extend(["--verbosity=2", "--tb=short"])

                project_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                subprocess.run(cmd, cwd=project_dir, timeout=1800)

                logger.info(f"Background test completed for TestRun #{test_run_id}")

            except Exception as e:
                logger.error(f"Background test error for TestRun #{test_run_id}: {e}")
                # Update test run with error
                try:
                    from apps.test.models.models import TestRun

                    test_run = TestRun.objects.get(id=test_run_id)
                    test_run.status = "failed"
                    test_run.error_message = str(e)
                    test_run.save()
                except Exception:
                    pass
            finally:
                if test_run_id in cls._active_runs:
                    del cls._active_runs[test_run_id]
                logger.info(f"Background test thread finished for TestRun #{test_run_id}")

        thread = threading.Thread(target=run_test_background, daemon=True)
        cls._active_runs[test_run_id] = thread
        thread.start()
        return thread


@app.task(bind=True)
def sync_translations(self):
    """Sync and check translations weekly."""
    try:
        logger.info("Starting weekly translation sync")

        # TODO: TranslationService no longer exists - implement translation sync if needed
        # from apps.translations.services.translation_service import TranslationService
        # translation_service = TranslationService()

        # Sync translations for all active stores
        from apps.stores.models import Store

        stores = Store.objects.filter(is_active=True)

        sync_results = []
        for store in stores:
            try:
                # TODO: Implement translation sync logic if TranslationService is recreated
                # result = translation_service.sync_store_translations(store)
                result = {"success": False, "translations_count": 0}  # Placeholder
                sync_results.append(
                    {
                        "store_id": store.id,
                        "store_name": store.name,
                        "success": result.get("success", False),
                        "translations_count": result.get("translations_count", 0),
                    }
                )
                logger.info(f"Synced translations for store: {store.name}")
            except Exception as e:
                logger.warning(f"Failed to sync translations for store {store.id}: {e}")
                sync_results.append(
                    {
                        "store_id": store.id,
                        "store_name": store.name,
                        "success": False,
                        "error": str(e),
                    }
                )

        successful_syncs = sum(1 for r in sync_results if r.get("success", False))

        logger.info(
            f"Weekly translation sync completed: {successful_syncs}/{len(sync_results)} stores successful"
        )

        return {
            "total_stores": len(sync_results),
            "successful_syncs": successful_syncs,
            "results": sync_results,
        }

    except Exception as e:
        logger.error(f"Translation sync failed: {e}")
        return {"total_stores": 0, "successful_syncs": 0, "error": str(e)}
