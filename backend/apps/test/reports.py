"""
Report generation utilities.
"""

from django.template.loader import render_to_string

from .models import TestResult, TestRun


def generate_html_report(test_run):
    """Generate HTML report for a test run"""
    results = TestResult.objects.filter(test_run=test_run)

    # Group results by app
    apps = {}
    for result in results:
        if result.app_name not in apps:
            apps[result.app_name] = []
        apps[result.app_name].append(result)

    # Group by endpoint
    for app_name, app_results in apps.items():
        endpoints = {}
        for result in app_results:
            if result.endpoint not in endpoints:
                endpoints[result.endpoint] = []
            endpoints[result.endpoint].append(result)
        apps[app_name] = endpoints

    # Group by role
    for app_name, endpoints in apps.items():
        for endpoint, endpoint_results in endpoints.items():
            roles = {}
            for result in endpoint_results:
                if result.role not in roles:
                    roles[result.role] = []
                roles[result.role].append(result)
            endpoints[endpoint] = roles

    # Generate HTML
    html = render_to_string(
        "test_report.html",
        {
            "test_run": test_run,
            "apps": apps,
            "total_tests": test_run.total_tests,
            "passed_tests": test_run.passed_tests,
            "failed_tests": test_run.failed_tests,
            "success_rate": test_run.success_rate,
            "duration_seconds": test_run.duration_seconds,
            "started_at": test_run.started_at,
            "completed_at": test_run.completed_at,
        },
    )

    return html
