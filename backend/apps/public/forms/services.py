"""
Services for forms module.
"""
from django.core.exceptions import ValidationError
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class FormService:
    """Shared form management service"""
    
    @staticmethod
    @transaction.atomic
    def submit_form(form_template, data, request):
        """Process form submission with validation"""
        # Ensure form is active and published before accepting submissions
        if form_template.status != 'published' or not form_template.is_active:
            raise ValidationError({'status': 'Form is not accepting submissions'})

        # Validate submission data
        errors = form_template.validate_submission_data(data)
        if errors:
            raise ValidationError(errors)
        
        # Create submission
        from .models import FormSubmission
        from apps.mediafile.models import MediaFile

        submission = FormSubmission.objects.create(
            form_template=form_template,
            data=data,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            status='pending'
        )
        
        # Attach media files if provided (basic attachment handling)
        attachment_ids = request.data.get('attachments') if hasattr(request, 'data') else None
        if attachment_ids:
            if isinstance(attachment_ids, str):
                attachment_ids = [attachment_ids]
            files = MediaFile.objects.filter(id__in=attachment_ids, store=form_template.store)
            if files.exists():
                submission.attachments.add(*files)

        # Log submission
        from apps.logs.tasks import log_event_async
        log_event_async.delay({
            'event_type': 'FORM_SUBMITTED',
            'message': f"Form submitted: {form_template.title}",
            'store': form_template.store,
            'user': request.user if request.user.is_authenticated else None,
            'entity_type': 'form_submission',
            'entity_id': submission.id,
            'metadata': {
                'form_title': form_template.title,
                'submission_id': submission.id
            }
        })
        
        # Trigger email notifications
        if form_template.send_email_notifications:
            from .tasks import send_form_notifications
            send_form_notifications.delay(submission.id)
        
        return submission
    
    @staticmethod
    def duplicate_form(form_template, user):
        """Duplicate form template with new slug"""
        from django.utils.text import slugify
        
        new_title = f"{form_template.title} (Copy)"
        new_slug = slugify(new_title)
        
        # Ensure unique slug
        counter = 1
        original_slug = new_slug
        while form_template.__class__.objects.filter(store=form_template.store, slug=new_slug).exists():
            new_slug = f"{original_slug}-{counter}"
            counter += 1
        
        new_form = form_template.__class__.objects.create(
            store=form_template.store,
            title=new_title,
            slug=new_slug,
            description=form_template.description,
            fields=form_template.fields,
            settings=form_template.settings,
            status='draft',
            created_by=user
        )
        
        # Duplicate email templates
        for email_template in form_template.email_templates.all():
            email_template.__class__.objects.create(
                store=new_form.store,
                form_template=new_form,
                title=email_template.title,
                subject=email_template.subject,
                body_html=email_template.body_html,
                body_text=email_template.body_text,
                headers=email_template.headers,
                variables=email_template.variables,
                recipient_type=email_template.recipient_type,
                recipient_email=email_template.recipient_email,
                auto_detect_recipient=email_template.auto_detect_recipient
            )
        
        from apps.logs.tasks import log_event_async
        log_event_async.delay({
            'user': user,
            'store': new_form.store,
            'action': 'form_duplicated',
            'object_type': 'form_template',
            'object_id': new_form.id,
            'details': {
                'original_form_id': form_template.id,
                'new_form_title': new_form.title
            }
        })
        
        return new_form
