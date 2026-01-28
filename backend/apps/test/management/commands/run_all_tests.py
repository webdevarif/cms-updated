"""
Management command to run all tests.
"""
from django.core.management.base import BaseCommand
from django.test.utils import get_runner

from ..runners.global_runner import GlobalTestRunner


class Command(BaseCommand):
    help = "Run all tests and generate HTML report"

    def add_arguments(self, parser):
        parser.add_argument("--html-report", action="store_true", help="Generate HTML report")
        parser.add_argument(
            "--html",
            type=str,
            default="report.html",
            help="HTML report file path (default: report.html)",
        )
        parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
        parser.add_argument(
            "--parallel", action="store_true", help="Run tests in parallel (requires pytest-xdist)"
        )
        parser.add_argument("--app", type=str, help="Test specific app (e.g., --app=stores)")
        parser.add_argument("--role", type=str, help="Test specific role (e.g., --role=admin)")
        parser.add_argument("--apps", nargs="*", help="Specific apps to test (default: all)")

    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model

        # Get or create admin user
        admin_user, _ = get_user_model.objects.get_or_create(
            email="admin@example.com", defaults={"is_staff": True, "is_superuser": True}
        )

        # Run tests
        runner = GlobalTestRunner(store=None, initiated_by=admin_user)  # Global test run

        if options["app"]:
            # Test specific app
            test_run = runner.run_app_tests(options["app"], role=options.get("role"))
        elif options["apps"]:
            # Test specific apps
            test_run = runner.run_specific_tests(options["apps"], role=options.get("role"))
        else:
            # Run all tests
            test_run = runner.run_all_tests()

        # Generate HTML report if requested
        if options["html_report"] or options["html"]:
            from ..reports import generate_html_report

            html = generate_html_report(test_run)

            # Save to file
            report_path = options["html"]
            with open(report_path, "w") as f:
                f.write(html)

            test_run.report_path = report_path
            test_run.html_report = html
            test_run.save()

        # Generate coverage report if requested
        if options["coverage"]:
            import subprocess

            self.stdout.write("Generating coverage report...")
            subprocess.run(["coverage", "run"])
            subprocess.run(["coverage", "html"])
            self.stdout.write(self.style.SUCCESS("Coverage report generated in htmlcov/"))

        # Generate pytest-html report if specified
        if options.get("html"):
            import subprocess

            self.stdout.write(f'Generating pytest-html report to {options["html"]}...')
            subprocess.run(["pytest", "--html=" + options["html"]])
            self.stdout.write(self.style.SUCCESS("pytest-html report generated"))

        self.stdout.write(f"Test run completed: {test_run.id}")
        self.stdout.write(f"Passed: {test_run.passed_tests}/{test_run.total_tests}")
        self.stdout.write(f"Success rate: {test_run.success_rate:.1f}%")
