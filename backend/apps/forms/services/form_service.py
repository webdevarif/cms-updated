"""
Form service for handling form operations.
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
import logging

from apps.forms.models import FormTemplate, FormSubmission

logger = logging.getLogger(__name__)


class FormService:
    """Service class for form operations."""
    
    @staticmethod
    def submit_form(form_template, submission_data, user=None, ip_address=None, user_agent=None):
        """
        Process a form submission.
        """
        try:
            # Create submission record
            submission = FormSubmission.objects.create(
                form_template=form_template,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                status='pending',
                metadata=submission_data.get('metadata', {})
            )
            
            # Create submission data records
            for field_name, field_value in submission_data.get('data', {}).items():
                FormSubmissionData.objects.create(
                    submission=submission,
                    field_name=field_name,
                    field_value=str(field_value),
                    field_type=submission_data.get('field_types', {}).get(field_name, 'text')
                )
            
            # Process the submission
            FormService._process_submission(submission)
            
            return submission
            
        except Exception as e:
            logger.error(f"Error submitting form: {str(e)}")
            raise
    
    @staticmethod
    def _process_submission(submission):
        """Process a form submission (send notifications, etc.)."""
        try:
            submission.status = 'processing'
            submission.save()
            
            # Send email notifications if enabled
            if submission.form_template.send_email_notifications:
                FormService._send_notification_email(submission)
            
            # Mark as completed
            submission.status = 'completed'
            submission.processed_at = timezone.now()
            submission.save()
            
        except Exception as e:
            logger.error(f"Error processing submission {submission.submission_id}: {str(e)}")
            submission.status = 'failed'
            submission.error_message = str(e)
            submission.processed_at = timezone.now()
            submission.save()
    
    @staticmethod
    def _send_notification_email(submission):
        """Send notification email for form submission."""
        try:
            subject = f"New Form Submission: {submission.form_template.title}"
            
            # Get store email from settings or use default
            store_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
            
            # Create email content
            context = {
                'submission': submission,
                'form_template': submission.form_template,
                'site_name': getattr(settings, 'SITE_NAME', 'Website'),
                'submission_url': f"{settings.SITE_URL}/forms/submissions/{submission.submission_id}/"
            }
            
            html_content = render_to_string('forms/email_notification.html', context)
            
            # Send to form template creator or store owner
            recipient_email = submission.form_template.created_by.email if submission.form_template.created_by else store_email
            
            send_mail(
                subject=subject,
                message=html_content,
                from_email=store_email,
                recipient_list=[recipient_email],
                html_message=html_content
            )
            
        except Exception as e:
            logger.error(f"Error sending notification email: {str(e)}")
    
    @staticmethod
    def get_form_statistics(form_template):
        """Get statistics for a form template."""
        return {
            'total_submissions': form_template.submissions.count(),
            'pending_submissions': form_template.submissions.filter(status='pending').count(),
            'completed_submissions': form_template.submissions.filter(status='completed').count(),
            'failed_submissions': form_template.submissions.filter(status='failed').count(),
            'recent_submissions': form_template.submissions.order_by('-submitted_at')[:10]
        }
