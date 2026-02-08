"""
Form service for handling form operations.

This service handles:
- Submission creation and processing
- Email notification sending
- Analytics and statistics helpers
"""

import logging

from apps.forms.models import FormSubmission, FormSubmissionData, FormTemplate

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


class FormService:
    """
    Service class for form operations.

    This service handles:
    - Submission creation and processing
    - Email notification sending
    - Analytics and statistics helpers

    All methods are static to provide a clean API without requiring instantiation.
    """

    # Submission handling methods
    @staticmethod
    def submit_form(form_template, submission_data, user=None, ip_address=None, user_agent=None):
        """
        Process a form submission.

        Creates submission record, stores field data, and triggers processing.
        """
        try:
            # Create submission record
            submission = FormSubmission.objects.create(
                form_template=form_template,
                store=form_template.store,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                status="pending",
                metadata=submission_data.get("metadata", {}),
            )

            # Create submission data records
            for field_name, field_value in submission_data.get("data", {}).items():
                FormSubmissionData.objects.create(
                    submission=submission,
                    field_name=field_name,
                    field_value=str(field_value),
                    field_type=submission_data.get("field_types", {}).get(field_name, "text"),
                )

            # Process the submission
            FormService._process_submission(submission)

            return submission

        except Exception as e:
            logger.error(f"Error submitting form: {str(e)}")
            raise

    @staticmethod
    def _process_submission(submission):
        """
        Process a form submission (send notifications, etc.).

        Updates submission status and triggers email notifications.
        """
        try:
            submission.status = "processing"
            submission.save()

            # Send email notifications if enabled
            if submission.form_template.send_email_notifications:
                FormService._send_notification_email(submission)

            # Mark as completed
            submission.status = "completed"
            submission.processed_at = timezone.now()
            submission.save()

        except Exception as e:
            logger.error(f"Error processing submission {submission.submission_id}: {str(e)}")
            submission.status = "failed"
            submission.error_message = str(e)
            submission.processed_at = timezone.now()
            submission.save()

    # Notification methods
    @staticmethod
    def _send_notification_email(submission):
        """Send notification email for form submission using email helper."""
        try:
            from .email_helper import send_form_notification

            # Create email context
            context = {
                "submission": submission,
                "form_template": submission.form_template,
                "site_name": getattr(settings, "SITE_NAME", "Website"),
                "submission_url": f"{settings.SITE_URL}/forms/submissions/{submission.submission_id}/",
                "recipient_email": (
                    submission.form_template.created_by.email
                    if submission.form_template.created_by
                    else getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")
                ),
            }

            # Send email using helper
            result = send_form_notification(submission.form_template, context)

            if not result["success"]:
                logger.error(f"Failed to send notification email: {result['message']}")

        except Exception as e:
            logger.error(f"Error in _send_notification_email: {str(e)}")

    # Statistics and analytics methods
    @staticmethod
    def get_form_analytics(form_template):
        """
        Get comprehensive analytics for a form template.

        Args:
            form_template: FormTemplate instance

        Returns:
            dict: Enhanced analytics including submission counts, user statistics, and trends
        """
        from .form_analytics_service import get_form_analytics as analytics_helper

        return analytics_helper(form_template)

    @staticmethod
    def get_form_statistics(form_template):
        """
        Get basic statistics for a form template.

        Args:
            form_template: FormTemplate instance

        Returns:
            dict: Basic counts and recent submissions
        """
        from .form_analytics_service import get_form_statistics as stats_helper

        return stats_helper(form_template)
