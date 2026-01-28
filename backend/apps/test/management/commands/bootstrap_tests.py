"""
Management command to bootstrap test.py files in all apps.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Bootstrap test.py files in all apps"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Show what would be created")

    def handle(self, *args, **options):
        import os

        from django.conf import settings

        apps = settings.INSTALLED_APPS
        test_apps = [app for app in apps if app.startswith("apps.")]

        for app in test_apps:
            app_path = app.replace(".", "/")
            test_file = f"{app_path}/tests/__init__.py"

            if os.path.exists(test_file):
                self.stdout.write(f"Test file already exists: {test_file}")
                continue

            if not options["dry_run"]:
                # Create test file
                os.makedirs(os.path.dirname(test_file), exist_ok=True)
                with open(test_file, "w") as f:
                    f.write(f'"""Tests for {app} module."""\n')
                    f.write(f"import pytest\n\n")
                    f.write(f"class Test{app.title()}(pytest.TestCase):\n")
                    f.write(f"    pass\n")
