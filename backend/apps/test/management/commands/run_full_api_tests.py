"""
Management command to run full API test suite with coverage.
"""

import subprocess

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run full API test suite with coverage"

    def add_arguments(self, parser):
        parser.add_argument("--html", action="store_true", help="Generate HTML test report")
        parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
        parser.add_argument(
            "--app", type=str, help="Test specific app only (e.g., stores, accounts)"
        )
        parser.add_argument(
            "--parallel",
            action="store_true",
            help="Run tests in parallel (requires pytest-xdist)",
        )

    def handle(self, *args, **options):
        # Build pytest command
        pytest_cmd = ["pytest"]

        # Add parallel flag if requested
        if options["parallel"]:
            pytest_cmd.extend(["-n", "auto"])

        # Add coverage if requested
        if options["coverage"]:
            pytest_cmd.extend(["--cov=apps", "--cov-report=html", "--cov-report=term"])

        # Add HTML report if requested
        if options["html"]:
            pytest_cmd.append("--html=test_report.html")

        # Add app filter if specified
        if options["app"]:
            pytest_cmd.append(f'apps/{options["app"]}/tests/')
        else:
            pytest_cmd.append("apps/")

        # Run pytest
        self.stdout.write("Running API tests...")
        result = subprocess.run(pytest_cmd)

        if result.returncode == 0:
            self.stdout.write(self.style.SUCCESS("All tests passed!"))
        else:
            self.stdout.write(self.style.ERROR("Some tests failed"))

        if options["coverage"]:
            self.stdout.write(self.style.SUCCESS("Coverage report generated in htmlcov/"))

        if options["html"]:
            self.stdout.write(self.style.SUCCESS("HTML report generated: test_report.html"))
