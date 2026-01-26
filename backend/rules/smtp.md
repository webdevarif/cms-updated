# Smtp Rules v1.0

## 🎯 Purpose
[Purpose content to be added]

## 🏗️ Structure
```
apps/backend/modules/smtp/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── migrations/
├── tasks.py
└── v1/
    ├── __init__.py
    ├── forms/
    ├── services.py
    ├── urls.py
    └── views/
        ├── __init__.py
        ├── configs.py
        ├── emails.py
        └── templates.py
```

## 🔧 Implementation
### 6.1 Password Encryption
```python
# models.py
from fernet_fields import EncryptedCharField

class SmtpConfiguration(models.Model):
    # ... other fields ...
    password = EncryptedCharField(max_length=255)
    
    def get_decrypted_password(self):
        """Get decrypted password for SMTP auth"""
        return self.password
```
### 6.2 Rate Limiting
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'emails': '100/hour',  # Per store
        'smtp_test': '10/hour',  # SMTP connection tests
    }
}

# views/configs.py
from rest_framework.throttling import UserRateThrottle

class EmailRateThrottle(UserRateThrottle):
    scope = 'emails'
    
    def get_cache_key(self, request, view):
        # Rate limit by store
        store_id = request.store.id if hasattr(request, 'store') else 'anon'
        return f'throttle_emails_{store_id}_{self.get_ident(request)}'
```

## 🔒 Permissions
### 6.1 Password Encryption
```python
# models.py
from fernet_fields import EncryptedCharField

class SmtpConfiguration(models.Model):
    # ... other fields ...
    password = EncryptedCharField(max_length=255)
    
    def get_decrypted_password(self):
        """Get decrypted password for SMTP auth"""
        return self.password
```
### 6.2 Rate Limiting
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'emails': '100/hour',  # Per store
        'smtp_test': '10/hour',  # SMTP connection tests
    }
}

# views/configs.py
from rest_framework.throttling import UserRateThrottle

class EmailRateThrottle(UserRateThrottle):
    scope = 'emails'
    
    def get_cache_key(self, request, view):
        # Rate limit by store
        store_id = request.store.id if hasattr(request, 'store') else 'anon'
        return f'throttle_emails_{store_id}_{self.get_ident(request)}'
```

## 🧪 Testing
config = self.get_object()
        try:
            is_valid = SmtpService.test_connection(config)
            return Response({
                'success': is_valid,
                'message': 'Connection successful' if is_valid else 'Connection failed'
            })
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
```

## ⚙️ Services
### 3.1 EmailService with Logging
```python
# v1/services.py
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail as django_send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from apps.logs.services import log_event_async

class EmailService:
    @classmethod
    def send_email(
        cls,
        to_email: str,
        subject: str,
        html_content: str = "",
        text_content: str = "",
        from_email: str = None,
        smtp_config_id: str = None,
        store=None,
        user=None,
        template_id: str = None,
        context: dict = None
    ) -> dict:
        """
        Send email using specified SMTP configuration with full logging
        """
        log_data = {
            'to_email': to_email,
            'subject': subject,
            'template_id': str(template_id) if template_id else None,
            'smtp_config_id': str(smtp_config_id) if smtp_config_id else None,
            'store_id': str(store.id) if store else None,
            'user_id': str(user.id) if user else None
        }
        
        try:
            # Get SMTP config (implementation omitted for brevity)
            smtp_config = cls._get_smtp_config(smtp_config_id, store)
            
            # Log email sending attempt
            log_event_async.delay(
                event_type='EMAIL_SEND_ATTEMPT',
                message=f"Sending email to {to_email}",
                store=store,
                user=user,
                metadata=log_data
            )
            
            # Send email (implementation details)
            result = django_send_mail(
                subject=subject,
                message=text_content,
                from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                html_message=html_content,
                fail_silently=False,
                auth_user=smtp_config.username,
                auth_password=smtp_config.get_decrypted_password(),
                connection=smtp_config.get_connection()
            )
            
            # Log success
            log_event_async.delay(
                event_type='EMAIL_SEND_SUCCESS',
                message=f"Email sent to {to_email}",
                store=store,
                user=user,
                metadata={
                    **log_data,
                    'message_id': result.message_id if hasattr(result, 'message_id') else None
                }
            )
            
            return {'success': True, 'message_id': getattr(result, 'message_id', None)}
            
        except Exception as e:
            # Log failure
            log_event_async.delay(
                event_type='EMAIL_SEND_FAILED',
                message=f"Failed to send email to {to_email}: {str(e)}",
                level='ERROR',
                store=store,
                user=user,
                metadata={
                    **log_data,
                    'error': str(e),
                    'error_type': e.__class__.__name__
                }
            )
            raise

    @staticmethod
    @shared_task(bind=True, max_retries=3)
    def send_email_async(self, email_data):
        """Celery task for async email sending"""
        try:
            return EmailService.send_email(**email_data)
        except Exception as exc:
            self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

## 🔗 Dependencies
[Dependencies content to be added]

## 📋 Migration
### 5.1 Management Command: migrate_smtp.py
```python
# management/commands/migrate_smtp.py
from django.core.management.base import BaseCommand
from django.db import transaction
from legacy_app.models import LegacySmtpConfig
from ...models import SmtpConfiguration

class Command(BaseCommand):
    help = 'Migrate SMTP configurations from legacy system'
    
    def handle(self, *args, **options):
        count = 0
        
        for legacy in LegacySmtpConfig.objects.all():
            try:
                with transaction.atomic():
                    config = SmtpConfiguration.objects.create(
                        name=legacy.config_name,
                        provider=self._map_provider(legacy.provider_type),
                        host=legacy.smtp_host,
                        port=legacy.smtp_port or 587,
                        username=legacy.username,
                        password=legacy.encrypted_password,  # Assumes decryption handled
                        use_tls=legacy.use_tls,
                        use_ssl=legacy.use_ssl,
                        store_id=legacy.store_id,
                        is_default=legacy.is_primary,
                        is_verified=legacy.is_verified
                    )
                    count += 1
                    self.stdout.write(f"Migrated SMTP config: {config.name}")
                    
            except Exception as e:
                self.stderr.write(f"Error migrating {legacy.config_name}: {str(e)}")
        
        self.stdout.write(self.style.SUCCESS(f'Successfully migrated {count} SMTP configurations'))
    
    def _map_provider(self, legacy_provider):
        """Map legacy provider names to new ones"""
        provider_map = {
            'google': 'gmail',
            'office365': 'outlook',
            'sendgrid': 'sendgrid',
            'custom': 'custom'
        }
        return provider_map.get(legacy_provider.lower(), 'custom')
```

## ✅ Benefits
[Benefits content to be added]

---
**Version**: 1.0  
**Last Updated**: 2026-01-26
**Next Review**: 2026-02-25
