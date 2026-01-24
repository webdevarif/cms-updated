"""
Services for forms app v2.

Business logic for form processing and management.
"""
import logging
from django.db import models

logger = logging.getLogger(__name__)


class FormService:
    """Form processing and management service"""
    
    @staticmethod
    def create_form(store, user, data):
        """Create a new form template"""
        from ..models.forms import FormTemplate
        from apps.logs.tasks import log_event_async
        
        # Generate unique form ID
        import random
        import string
        form_id = ''.join(random.choices(string.digits, k=6))
        
        # Ensure form_id is unique using centralized service
        from core.services.base import BaseTenantCRUDService
        BaseTenantCRUDService.model_class = FormTemplate
        while BaseTenantCRUDService.filter(form_id=form_id).exists():
            form_id = ''.join(random.choices(string.digits, k=6))
        
        # Create form template using centralized service
        form = BaseTenantCRUDService.create(
            store=store,
            title=data.get('title', ''),
            slug=data.get('slug', ''),
            description=data.get('description', ''),
            form_id=form_id,
            fields=data.get('fields', {}),
            settings=data.get('settings', {}),
            status='draft',
            save_to_database=data.get('save_to_database', True),
            send_email_notifications=data.get('send_email_notifications', True)
        )
        
        log_event_async.delay({
            'event_type': 'FORM_CREATED',
            'message': f"Form created: {form.title}",
            'store': store,
            'user': user,
            'entity_type': 'FormTemplate',
            'entity_id': form.id,
            'metadata': {
                'form_id': form.form_id,
                'title': form.title
            }
        })
        
        return form
    
    @staticmethod
    def process_submission(store, form, data, user=None):
        """Process form submission"""
        from ..models.submissions import FormSubmission, FormSubmissionData
        from apps.logs.tasks import log_event_async
        
        # Validate form data
        validation_result = FormService.validate_form_data(form, data)
        if not validation_result['valid']:
            return {'success': False, 'errors': validation_result['errors']}
        
        # Create submission using centralized service
        from core.services.base import BaseTenantCRUDService
        BaseTenantCRUDService.model_class = FormSubmission
        submission = BaseTenantCRUDService.create(
            store=store,
            form=form,
            user=user,
            ip_address=data.get('ip_address', ''),
            user_agent=data.get('user_agent', ''),
            status='submitted'
        )
        
        # Save submission data using centralized service
        BaseTenantCRUDService.model_class = FormSubmissionData
        for field_name, field_value in data.get('form_data', {}).items():
            BaseTenantCRUDService.create(
                submission=submission,
                field_name=field_name,
                field_value=field_value
            )
        
        # Send email notifications if enabled
        if form.send_email_notifications:
            # Use centralized email service
            from core.libs.email import EmailService
            try:
                EmailService.send_form_notification(form, submission)
                # Also send auto-reply if enabled
                EmailService.send_auto_reply(form, submission)
            except Exception as e:
                logger.error(f"Failed to send form notification email: {e}")
        
        log_event_async.delay({
            'event_type': 'FORM_SUBMITTED',
            'message': f"Form submitted: {form.title}",
            'store': store,
            'user': user,
            'entity_type': 'FormSubmission',
            'entity_id': submission.id,
            'metadata': {
                'form_id': form.form_id,
                'submission_id': submission.id
            }
        })
        
        return {'success': True, 'submission_id': submission.id}
    
    @staticmethod
    def validate_form_data(form, data):
        """Validate form data against form fields"""
        errors = {}
        form_data = data.get('form_data', {})
        fields = form.fields
        
        # Validate required fields
        for field_name, field_config in fields.items():
            if field_config.get('required', False) and not form_data.get(field_name):
                field_label = field_config.get('label', field_name)
                errors[field_name] = f"{field_label} is required"
        
        # Validate field types and constraints
        for field_name, field_value in form_data.items():
            if field_name in fields:
                field_config = fields[field_name]
                field_type = field_config.get('type')
                
                # Email validation
                if field_type == 'email' and field_value:
                    import re
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if not re.match(email_pattern, field_value):
                        field_label = field_config.get('label', field_name)
                        errors[field_name] = f"{field_label} must be a valid email address"
                
                # Number validation
                elif field_type == 'number' and field_value:
                    try:
                        num_value = float(field_value)
                        min_val = field_config.get('min_value')
                        max_val = field_config.get('max_value')
                        
                        if min_val is not None and num_value < min_val:
                            field_label = field_config.get('label', field_name)
                            errors[field_name] = f"{field_label} must be at least {min_val}"
                        
                        if max_val is not None and num_value > max_val:
                            field_label = field_config.get('label', field_name)
                            errors[field_name] = f"{field_label} must be at most {max_val}"
                            

                # URL validation
                elif field_type == 'url' and field_value:
                    from django.core.validators import URLValidator
                    validator = URLValidator()
                    try:
                        validator(field_value)
                    except:
                        field_label = field_config.get('label', field_name)
                        errors[field_name] = f"{field_label} must be a valid URL"
                
                # Phone validation
                elif field_type == 'phone' and field_value:
                    import re
                    phone_pattern = r'^[\d\s\-\+\(\)]+$'
                    if not re.match(phone_pattern, field_value) or len(field_value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')) < 10:
                        field_label = field_config.get('label', field_name)
                        errors[field_name] = f"{field_label} must be a valid phone number"
                
                # Date validation
                elif field_type == 'date' and field_value:
                    from datetime import datetime
                    try:
                        datetime.strptime(field_value, '%Y-%m-%d')
                    except ValueError:
                        field_label = field_config.get('label', field_name)
                        errors[field_name] = f"{field_label} must be a valid date (YYYY-MM-DD)"
                
                # File validation
                elif field_type == 'file' and field_value:
                    if isinstance(field_value, list):
                        for file_id in field_value:
                            if not isinstance(file_id, (int, str)):
                                field_label = field_config.get('label', field_name)
                                errors[field_name] = f"{field_label} contains invalid file references"
                    else:
                        field_label = field_config.get('label', field_name)
                        errors[field_name] = f"{field_label} must contain file references"
                
                # Text length validation
                elif field_type in ['text', 'textarea'] and field_value:
                    min_length = field_config.get('min_length')
                    max_length = field_config.get('max_length', 1000)
                    
                    if min_length is not None and len(field_value) < min_length:
                        field_label = field_config.get('label', field_name)
                        errors[field_name] = f"{field_label} must be at least {min_length} characters"
                    
                    if len(field_value) > max_length:
                        field_label = field_config.get('label', field_name)
                        errors[field_name] = f"{field_label} must be at most {max_length} characters"
                
                # Select/Checkbox validation
                elif field_type in ['select', 'checkbox'] and field_value:
                    options = field_config.get('options', [])
                    if isinstance(field_value, list):
                        for val in field_value:
                            if val not in options:
                                field_label = field_config.get('label', field_name)
                                errors[field_name] = f"{field_label} contains invalid option: {val}"
                    else:
                        if field_value not in options:
                            field_label = field_config.get('label', field_name)
                            errors[field_name] = f"{field_label} contains invalid option: {field_value}"
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    @staticmethod
    def validate_form_template(form_data):
        """
        Validate form template configuration
        
        Args:
            form_data: Form template data
            
        Returns:
            dict: Validation result with errors if any
        """
        errors = {}
        
        # Validate required fields
        if not form_data.get('title'):
            errors['title'] = 'Form title is required'
        
        if not form_data.get('slug'):
            errors['slug'] = 'Form slug is required'
        elif not form_data['slug'].replace('-', '').replace('_', '').isalnum():
            errors['slug'] = 'Slug must contain only letters, numbers, hyphens, and underscores'
        
        # Validate fields configuration
        fields = form_data.get('fields', {})
        if not fields:
            errors['fields'] = 'Form must have at least one field'
        else:
            for field_name, field_config in fields.items():
                field_errors = FormService._validate_field_config(field_name, field_config)
                if field_errors:
                    errors[f'field_{field_name}'] = field_errors
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    @staticmethod
    def _validate_field_config(field_name, field_config):
        """
        Validate individual field configuration
        
        Args:
            field_name: Field name
            field_config: Field configuration dictionary
            
        Returns:
            dict: Field validation errors
        """
        errors = []
        
        if not isinstance(field_config, dict):
            return ['Field configuration must be a dictionary']
        
        # Required field properties
        if 'type' not in field_config:
            errors.append('Field type is required')
        
        if 'label' not in field_config:
            errors.append('Field label is required')
        
        # Validate field type
        valid_types = ['text', 'email', 'number', 'url', 'phone', 'date', 'textarea', 'select', 'checkbox', 'radio', 'file']
        field_type = field_config.get('type')
        if field_type and field_type not in valid_types:
            errors.append(f'Invalid field type: {field_type}')
        
        # Validate options for select/radio/checkbox
        if field_type in ['select', 'radio', 'checkbox']:
            options = field_config.get('options', [])
            if not options:
                errors.append(f'{field_type} field must have options')
            elif not isinstance(options, list):
                errors.append(f'{field_type} options must be a list')
        
        # Validate validation rules
        if field_type == 'number':
            min_val = field_config.get('min_value')
            max_val = field_config.get('max_value')
            
            if min_val is not None and max_val is not None and min_val > max_val:
                errors.append('min_value cannot be greater than max_value')
        
        if field_type in ['text', 'textarea']:
            min_length = field_config.get('min_length')
            max_length = field_config.get('max_length')
            
            if min_length is not None and max_length is not None and min_length > max_length:
                errors.append('min_length cannot be greater than max_length')
        
        return errors
    
    @staticmethod
    def duplicate_form(form_template, user):
        """
        Duplicate a form template with all its settings
        
        Args:
            form_template: FormTemplate instance to duplicate
            user: User creating the duplicate
            
        Returns:
            FormTemplate: New duplicated form
        """
        from core.services.base import BaseTenantCRUDService
        
        # Generate new unique slug and form_id
        import random
        import string
        
        new_title = f"{form_template.title} (Copy)"
        new_slug = f"{form_template.slug}-copy"
        
        # Ensure unique slug
        counter = 1
        original_slug = new_slug
        BaseTenantCRUDService.model_class = FormTemplate
        while BaseTenantCRUDService.filter(
            store=form_template.store,
            slug=new_slug
        ).exists():
            new_slug = f"{original_slug}-{counter}"
            counter += 1
        
        # Generate new form_id
        form_id = ''.join(random.choices(string.digits, k=6))
        while BaseTenantCRUDService.filter(form_id=form_id).exists():
            form_id = ''.join(random.choices(string.digits, k=6))
        
        # Create duplicate form
        new_form = BaseTenantCRUDService.create(
            store=form_template.store,
            title=new_title,
            slug=new_slug,
            description=form_template.description,
            form_id=form_id,
            fields=form_template.fields.copy(),
            settings=form_template.settings.copy(),
            status='draft',
            save_to_database=form_template.save_to_database,
            send_email_notifications=form_template.send_email_notifications,
            seo_title=form_template.seo_title,
            seo_description=form_template.seo_description,
        )
        
        # Log the duplication
        from apps.logs.tasks import log_event_async
        log_event_async.delay({
            'event_type': 'FORM_DUPLICATED',
            'message': f"Form duplicated: {new_form.title}",
            'store': form_template.store,
            'user': user,
            'entity_type': 'FormTemplate',
            'entity_id': new_form.id,
            'metadata': {
                'original_form_id': form_template.id,
                'original_title': form_template.title,
                'new_form_id': new_form.id,
                'new_title': new_form.title
            }
        })
        
        return new_form
    
    @staticmethod
    def get_form_statistics(form_template, days=30):
        """
        Get statistics for a specific form
        
        Args:
            form_template: FormTemplate instance
            days: Number of days to look back
            
        Returns:
            dict: Form statistics
        """
        from datetime import timedelta
        from django.utils import timezone
        from core.services.base import BaseTenantCRUDService
        
        since = timezone.now() - timedelta(days=days)
        
        BaseTenantCRUDService.model_class = FormSubmission
        submissions = BaseTenantCRUDService.filter(
            form_template=form_template,
            submitted_at__gte=since
        )
        
        # Basic stats
        total_submissions = submissions.count()
        
        # Status distribution
        status_distribution = submissions.values('status').annotate(
            count=models.Count('id')
        ).order_by('-count')
        
        # Daily submission trend
        daily_trend = submissions.extra({
            'date': models.DateField('submitted_at')
        }).values('date').annotate(
            count=models.Count('id')
        ).order_by('date')
        
        # Field completion rates
        field_completion = {}
        if total_submissions > 0:
            BaseTenantCRUDService.model_class = FormSubmissionData
            for field_name in form_template.fields.keys():
                completed = BaseTenantCRUDService.filter(
                    submission__form_template=form_template,
                    submission__submitted_at__gte=since,
                    field_name=field_name,
                    field_value__ne=''
                ).count()
                
                field_completion[field_name] = {
                    'completed': completed,
                    'rate': round((completed / total_submissions) * 100, 2)
                }
        
        return {
            'total_submissions': total_submissions,
            'period_days': days,
            'status_distribution': list(status_distribution),
            'daily_trend': list(daily_trend),
            'field_completion': field_completion,
            'average_per_day': round(total_submissions / days, 2),
        }
    
    @staticmethod
    def get_form_submissions(store, form_id):
        """Get all submissions for a form"""
        from ..models.forms import FormTemplate
        from ..models.submissions import FormSubmission
        
        try:
            from core.services.base import BaseTenantCRUDService
            BaseTenantCRUDService.model_class = FormTemplate
            form = BaseTenantCRUDService.get(store=store, id=form_id)
            
            BaseTenantCRUDService.model_class = FormSubmission
            submissions = BaseTenantCRUDService.filter(
                store=store,
                form=form
            ).order_by('-created_at').select_related('user')
            
            return {
                'form': form,
                'submissions': submissions,
                'count': submissions.count()
            }
        except FormTemplate.DoesNotExist:
            return None
    
    @staticmethod
    def update_form(form, data, user=None):
        """Update an existing form"""
        from apps.logs.tasks import log_event_async
        
        old_data = {
            'title': form.title,
            'description': form.description,
            'status': form.status
        }
        
        # Update fields
        for field, value in data.items():
            if hasattr(form, field) and field not in ['id', 'form_id', 'created_at', 'store']:
                setattr(form, field, value)
        
        form.save()
        
        log_event_async.delay({
            'event_type': 'FORM_UPDATED',
            'message': f"Form updated: {form.title}",
            'store': form.store,
            'user': user,
            'entity_type': 'FormTemplate',
            'entity_id': form.id,
            'metadata': {
                'form_id': form.form_id,
                'old_data': old_data,
                'new_data': data
            }
        })
        
        return form
    
    @staticmethod
    def delete_form(form, user=None):
        """Delete a form"""
        from apps.logs.tasks import log_event_async
        
        form_id = form.form_id
        title = form.title
        
        # Delete form using centralized service
        from core.services.base import BaseTenantCRUDService
        BaseTenantCRUDService.model_class = FormTemplate
        BaseTenantCRUDService.delete(form)
        
        log_event_async.delay({
            'event_type': 'FORM_DELETED',
            'message': f"Form deleted: {title}",
            'store': form.store,
            'user': user,
            'entity_type': 'FormTemplate',
            'entity_id': form.id,
            'metadata': {
                'form_id': form_id,
                'title': title
            }
        })
    
    @staticmethod
    def publish_form(form, user=None):
        """Publish a form"""
        from apps.logs.tasks import log_event_async
        
        form.status = 'published'
        form.save()
        
        log_event_async.delay({
            'event_type': 'FORM_PUBLISHED',
            'message': f"Form published: {form.title}",
            'store': form.store,
            'user': user,
            'entity_type': 'FormTemplate',
            'entity_id': form.id,
            'metadata': {
                'form_id': form.form_id,
                'title': form.title
            }
        })
        
        return form
    
    @staticmethod
    def send_form_notifications(submission_id):
        """
        Send email notifications for form submission
        
        Args:
            submission_id: ID of the form submission
            
        Returns:
            dict: Result of email sending operation
        """
        from ..models.submissions import FormSubmission
        from core.services.base import BaseTenantCRUDService
        
        try:
            BaseTenantCRUDService.model_class = FormSubmission
            submission = BaseTenantCRUDService.get(id=submission_id)
            
            # Use centralized email service if available
            try:
                from core.services.email import EmailService
                EmailService.send_form_notification(submission)
                return {'success': True, 'message': 'Notifications sent'}
            except ImportError:
                # Fallback to basic logging if email service not available
                logger.info(f"Form submission {submission_id} processed (email service not available)")
                return {'success': True, 'message': 'Processed (no email service)'}
                
        except Exception as e:
            logger.error(f"Failed to send notifications for submission {submission_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
