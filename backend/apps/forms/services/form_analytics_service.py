"""
Form analytics service for forms app.

Provides analytics and statistics for form templates and submissions.
"""

from django.db.models import Avg, Count, F


def get_form_analytics(form_template):
    """
    Get comprehensive analytics for a form template.

    Args:
        form_template: FormTemplate instance

    Returns:
        dict: Comprehensive analytics including submission counts, user statistics, and trends
    """
    from ..models.submissions import FormSubmission

    submissions = FormSubmission.objects.filter(form_template=form_template)

    # Basic counts
    total_submissions = submissions.count()
    pending_submissions = submissions.filter(status="pending").count()
    completed_submissions = submissions.filter(status="completed").count()
    failed_submissions = submissions.filter(status="failed").count()

    # User statistics
    unique_users = submissions.values("user").distinct().count()
    authenticated_submissions = submissions.filter(user__isnull=False).count()
    anonymous_submissions = submissions.filter(user__isnull=True).count()

    # Time-based analytics
    recent_submissions = list(
        submissions.order_by("-submitted_at")[:10].values(
            "submission_id",
            "user__username",
            "user__email",
            "status",
            "submitted_at",
            "processed_at",
        )
    )

    # Daily submission trends (last 30 days)
    from datetime import timedelta

    from django.utils import timezone

    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_submissions = list(
        submissions.filter(submitted_at__gte=thirty_days_ago)
        .extra({"date": "date(submitted_at)"})
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )

    return {
        "total_submissions": total_submissions,
        "pending_submissions": pending_submissions,
        "completed_submissions": completed_submissions,
        "failed_submissions": failed_submissions,
        "success_rate": (
            (completed_submissions / total_submissions * 100) if total_submissions > 0 else 0
        ),
        "unique_users": unique_users,
        "authenticated_submissions": authenticated_submissions,
        "anonymous_submissions": anonymous_submissions,
        "recent_submissions": recent_submissions,
        "daily_submissions": daily_submissions,
        "average_processing_time": _get_average_processing_time(submissions),
    }


def get_form_statistics(form_template):
    """
    Get basic statistics for a form template.

    Args:
        form_template: FormTemplate instance

    Returns:
        dict: Basic counts and recent submissions
    """
    from ..models.submissions import FormSubmission

    submissions = FormSubmission.objects.filter(form_template=form_template)

    return {
        "total_submissions": submissions.count(),
        "pending_submissions": submissions.filter(status="pending").count(),
        "completed_submissions": submissions.filter(status="completed").count(),
        "failed_submissions": submissions.filter(status="failed").count(),
        "recent_submissions": list(
            submissions.order_by("-submitted_at")[:10].values(
                "submission_id",
                "user__username",
                "user__email",
                "status",
                "submitted_at",
                "processed_at",
            )
        ),
    }


def _get_average_processing_time(submissions):
    """
    Calculate average processing time for completed submissions.

    Args:
        submissions: FormSubmission queryset

    Returns:
        float: Average processing time in minutes, or 0 if no completed submissions
    """
    completed_submissions = submissions.filter(status="completed", processed_at__isnull=False)

    if not completed_submissions.exists():
        return 0

    # Calculate processing time in minutes
    processing_times = []
    for submission in completed_submissions:
        if submission.processed_at and submission.submitted_at:
            processing_time = (
                submission.processed_at - submission.submitted_at
            ).total_seconds() / 60
            processing_times.append(processing_time)

    return sum(processing_times) / len(processing_times) if processing_times else 0
