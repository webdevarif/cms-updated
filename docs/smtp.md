# SMTP Module Rules v1.0

## 1. Directory Structure
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

## 2. Core Models

### 2.1 SmtpConfiguration
```python
class SmtpConfiguration(models.Model):
    PROVIDER_CHOICES = [
        ('gmail', 'Gmail'),
        ('outlook', 'Outlook'),
        ('sendgrid', 'SendGrid'),
        ('mailgun', 'Mailgun'),
        ('amazon_ses', 'Amazon SES'),
        ('custom', 'Custom SMTP'),
    ]

    # ... (keep existing fields)

    def save(self, *args, **kwargs):
        # Log configuration changes
        from apps.logs.services import log_event_async

        is_new = self._state.adding
        super().save(*args, **kwargs)

        log_event_async.delay(
            event_type='SMTP_CONFIG_SAVED' if not is_new else 'SMTP_CONFIG_CREATED',
            message=f"SMTP Config {'created' if is_new else 'updated'}: {self.name}",
            store=self.store,
            metadata={
                'config_id': str(self.id),
                'provider': self.provider,
                'is_default': self.is_default,
                'is_verified': self.is_verified
            }
        )
```

## 3. Services

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

## 4. Admin & Dashboard Views

### 4.1 admin.py
```python
from django.contrib import admin
from django.utils.html import format_html
from .models import SmtpConfiguration, EmailTemplate, EmailLog

@admin.register(SmtpConfiguration)
class SmtpConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'host', 'port', 'is_default', 'is_verified', 'store')
    list_filter = ('provider', 'is_default', 'is_verified', 'store')
    search_fields = ('name', 'host', 'username')
    readonly_fields = ('last_tested', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'provider', 'store', 'is_default')
        }),
        ('SMTP Settings', {
            'fields': ('host', 'port', 'username', 'password', 'use_tls', 'use_ssl')
        }),
        ('Status', {
            'fields': ('is_verified', 'last_tested')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        # Encrypt password before saving
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'subject', 'is_active', 'store')
    list_filter = ('template_type', 'is_active', 'store')
    search_fields = ('name', 'subject', 'html_content')
    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        # Log template changes
        from apps.logs.services import log_event_async
        action = 'created' if not change else 'updated'
        log_event_async.delay(
            event_type='EMAIL_TEMPLATE_SAVED',
            message=f"Email template {obj.name} {action}",
            store=obj.store,
            user=request.user,
            metadata={
                'template_id': str(obj.id),
                'template_type': obj.template_type,
                'changes': form.changed_data if change else None
            }
        )
        super().save_model(request, obj, form, change)

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('to_email', 'subject', 'status', 'sent_at', 'store')
    list_filter = ('status', 'sent_at', 'store')
    search_fields = ('to_email', 'subject', 'message_id')
    readonly_fields = ('sent_at', 'delivered_at', 'opened_at', 'created_at')
    date_hierarchy = 'sent_at'
```

### 4.2 Dashboard API Views
```python
# v1/views/configs.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ...models import SmtpConfiguration
from .serializers import SmtpConfigSerializer
from ...services import SmtpService

class SmtpConfigViewSet(viewsets.ModelViewSet):
    serializer_class = SmtpConfigSerializer
    permission_classes = [IsAuthenticated, IsStoreAdmin]

    def get_queryset(self):
        return SmtpConfiguration.objects.filter(store=self.request.store)

    def perform_create(self, serializer):
        serializer.save(store=self.request.store)

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test SMTP connection"""
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

## 5. Migration & Legacy Support

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

## 6. Security Implementation

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

## 7. Testing Examples

### 7.1 Test Email Sending
```python
# tests/test_emails.py
import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from ..services import EmailService

class TestEmailService(TestCase):
    @patch('django.core.mail.send_mail')
    def test_send_email_success(self, mock_send):
        # Setup
        mock_send.return_value = 1

        # Test
        result = EmailService.send_email(
            to_email='test@example.com',
            subject='Test',
            html_content='<p>Test</p>',
            text_content='Test'
        )

        # Assert
        self.assertTrue(result['success'])
        mock_send.assert_called_once()

    @patch('django.core.mail.send_mail')
    def test_send_email_failure(self, mock_send):
        # Setup
        mock_send.side_effect = Exception('SMTP Error')

        # Test & Assert
        with self.assertRaises(Exception):
            EmailService.send_email(
                to_email='test@example.com',
                subject='Test',
                html_content='<p>Test</p>'
            )
```

### 7.2 Test SMTP Configuration
```python
# tests/test_smtp_config.py
from django.test import TestCase
from ..models import SmtpConfiguration

class TestSmtpConfiguration(TestCase):
    def test_password_encryption(self):
        # Setup
        config = SmtpConfiguration.objects.create(
            name='Test Config',
            host='smtp.example.com',
            username='user',
            password='secret',
            use_tls=True
        )

        # Test
        saved_config = SmtpConfiguration.objects.get(pk=config.pk)

        # Assert
        self.assertNotEqual(saved_config.password, 'secret')  # Should be encrypted
        self.assertEqual(saved_config.get_decrypted_password(), 'secret')
```

## 8. Celery Tasks

### 8.1 tasks.py
```python
from celery import shared_task
from django.conf import settings
from .models import EmailQueue
from .services import EmailService
from apps.logs.services import log_event_async

@shared_task(bind=True, max_retries=3)
def process_email_queue(self):
    """Process queued emails"""
    batch_size = getattr(settings, 'EMAIL_BATCH_SIZE', 50)

    # Get pending emails, ordered by priority and creation time
    queued_emails = EmailQueue.objects.filter(
        is_processed=False,
        scheduled_at__lte=timezone.now()
    ).order_by('priority', 'created_at')[:batch_size]

    for email in queued_emails:
        try:
            # Add tracking if enabled
            if email.is_tracked and email.html_content:
                email.html_content = EmailService.add_tracking(email, email.html_content)

            # Send email
            result = EmailService.send_email_async.delay({
                'to_email': email.to_email,
                'subject': email.subject,
                'html_content': email.html_content,
                'text_content': email.text_content,
                'smtp_config_id': str(email.smtp_config_id),
                'store_id': str(email.store_id),
                'template_id': str(email.template_id) if email.template_id else None,
                'track_opens': email.is_tracked,
                'track_clicks': email.is_tracked,
                'tracking_id': str(email.tracking_id) if email.is_tracked else None
            })

            # Mark as processed
            email.is_processed = True
            email.processed_at = timezone.now()
            email.status = 'processing'
            email.save()

            # Log sent event
            email.add_tracking_event('sent', {
                'queue_id': str(email.id),
                'scheduled_at': str(email.scheduled_at)
            })

        except Exception as e:
            # Handle retries
            email.retry_count += 1
            if email.retry_count >= email.max_retries:
                email.is_processed = True
                email.status = 'failed'
                email.error_message = str(e)

                # Log failure
                email.add_tracking_event('failed', {
                    'error': str(e),
                    'retry_count': email.retry_count,
                    'max_retries': email.max_retries
                })

            email.save()

            # Log error
            log_event_async.delay(
                event_type='EMAIL_QUEUE_ERROR',
                message=f'Failed to process queued email: {str(e)}',
                store=email.store,
                metadata={
                    'email_id': str(email.id),
                    'to_email': email.to_email,
                    'retry_count': email.retry_count,
                    'error': str(e)
                },
                level='ERROR'
            )

            # Retry with exponential backoff
            raise self.retry(exc=e, countdown=60 * (2 ** email.retry_count))
```

## 9. Email Tracking & Analytics

### 9.1 Tracking Pixel Implementation
```python
# v1/views/tracking.py
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseNotFound
from django.utils import timezone
import base64
from ...models import EmailLog, EmailTracking

@csrf_exempt
@require_http_methods(['GET'])
def track_email_open(request, tracking_id):
    """
    Endpoint for tracking email opens via 1x1 pixel
    """
    try:
        email_log = EmailLog.objects.get(tracking_id=tracking_id)

        # Add tracking event
        email_log.add_tracking_event(
            event_type='opened',
            event_data={
                'ip': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT'),
                'referer': request.META.get('HTTP_REFERER')
            },
            request=request
        )

        # Return transparent 1x1 GIF
        pixel = base64.b64decode('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7')
        response = HttpResponse(pixel, content_type='image/gif')

        # Cache control headers
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

        return response

    except EmailLog.DoesNotExist:
        return HttpResponseNotFound()
```

### 9.2 Click Tracking
```python
# v1/services.py
import re
import urllib.parse
from bs4 import BeautifulSoup

class EmailService:
    # ... existing methods ...

    URL_PATTERN = re.compile(
        r'https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )

    @classmethod
    def add_click_tracking(cls, email_log, content, is_html=True):
        """
        Convert all links in the email to tracked links
        Supports both HTML and plain text emails
        """
        if not email_log.is_tracked or not content:
            return content

        if is_html:
            return cls._track_html_links(email_log, content)
        return cls._track_text_links(email_log, content)

    @classmethod
    def _track_html_links(cls, email_log, html_content):
        """Track links in HTML emails"""
        soup = BeautifulSoup(html_content, 'html.parser')

        for link in soup.find_all('a', href=True):
            original_url = link['href']
            if not original_url or not original_url.startswith(('http://', 'https://')):
                continue

            # Create tracking URL
            tracking_url = cls._create_tracking_url(email_log, original_url)

            # Update link
            link['href'] = tracking_url

            # Add tracking class and style (if not already present)
            if 'tracked-link' not in link.get('class', []):
                link['class'] = link.get('class', []) + ['tracked-link']

            # Ensure link is visible in email clients
            link_style = link.get('style', '')
            if 'color:' not in link_style:
                link_style = (link_style + ';color: #2563eb;').strip(';')
                link['style'] = link_style

        return str(soup)

    @classmethod
    def _track_text_links(cls, email_log, text_content):
        """Track links in plain text emails"""
        def replace_match(match):
            original_url = match.group(0)
            tracking_url = cls._create_tracking_url(email_log, original_url)
            return f"{original_url} [Tracked: {tracking_url}]"

        return cls.URL_PATTERN.sub(replace_match, text_content)

    @classmethod
    def _create_tracking_url(cls, email_log, original_url):
        """Create a tracking URL for click tracking"""
        from django.urls import reverse
        import hashlib

        # Generate URL-safe hash of the original URL
        url_hash = hashlib.md5(original_url.encode()).hexdigest()[:8]

        # Create tracking URL
        tracking_path = reverse('smtp:track-click', kwargs={
            'tracking_id': str(email_log.tracking_id),
            'url_hash': url_hash
        })

        # Encode original URL as query parameter
        encoded_url = urllib.parse.quote(original_url)
        return f"{settings.SITE_URL}{tracking_path}?url={encoded_url}"
```

### 9.3 Webhook Handler with Security

#### 9.3.1 Security Considerations
- **Webhook Verification**: All webhook requests must be verified using provider signatures
- **Rate Limiting**: Implement rate limiting to prevent abuse
- **IP Whitelisting**: Optionally restrict incoming webhooks to known provider IPs
- **Request Timeout**: Verify webhook timestamps to prevent replay attacks

#### 9.3.2 Implementation
```python
# v1/views/webhooks.py
import hmac
import hashlib
import json
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from ...models import EmailLog, EmailTracking

logger = logging.getLogger(__name__)

# Webhook configuration (move to settings.py in production)
WEBHOOK_CONFIG = {
    'sendgrid': {
        'signing_key': settings.SENDGRID_WEBHOOK_SIGNING_KEY,
        'signature_header': 'X-Twilio-Email-Event-Webhook-Signature',
        'timestamp_header': 'X-Twilio-Email-Event-Webhook-Timestamp',
        'max_age_seconds': 300,  # 5 minutes
    },
    'mailgun': {
        'signing_key': settings.MAILGUN_WEBHOOK_SIGNING_KEY,
        'signature_param': 'signature',
        'timestamp_param': 'timestamp',
        'token_param': 'token',
    }
}

@method_decorator(csrf_exempt, name='dispatch')
class EmailWebhookView(APIView):
    permission_classes = [AllowAny]

    def verify_webhook_signature(self, request, provider):
        """Verify webhook signature using provider's signing key"""
        config = WEBHOOK_CONFIG.get(provider, {})

        if provider == 'sendgrid':
            # Verify SendGrid signature
            signature = request.headers.get(config['signature_header'])
            timestamp = request.headers.get(config['timestamp_header'])

            if not all([signature, timestamp, config['signing_key']]):
                logger.warning('Missing required signature headers or signing key')
                return False

            # Verify timestamp (prevent replay attacks)
            try:
                event_time = datetime.fromtimestamp(int(timestamp))
                if (datetime.utcnow() - event_time) > timedelta(seconds=config['max_age_seconds']):
                    logger.warning('Webhook timestamp too old')
                    return False
            except (ValueError, TypeError):
                logger.warning('Invalid timestamp in webhook')
                return False

            # Verify signature
            payload = f"{timestamp}{request.body.decode('utf-8')}"
            expected_signature = hmac.new(
                key=config['signing_key'].encode('utf-8'),
                msg=payload.encode('utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)

        elif provider == 'mailgun':
            # Similar verification for Mailgun
            data = request.data
            signature = data.get(config['signature_param'])
            timestamp = data.get(config['timestamp_param'])
            token = data.get(config['token_param'])

            if not all([signature, timestamp, token, config['signing_key']]):
                return False

            # Verify timestamp (Mailgun uses seconds since epoch)
            try:
                if (time.time() - int(timestamp)) > config.get('max_age_seconds', 300):
                    return False
            except (ValueError, TypeError):
                return False

            # Verify signature
            signing_data = f"{timestamp}{token}"
            expected_signature = hmac.new(
                key=config['signing_key'].encode('utf-8'),
                msg=signing_data.encode('utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)

        return False  # Default to deny for unknown providers

    def post(self, request, provider=None, *args, **kwargs):
        """
        Handle email webhooks from various providers with signature verification
        """
        try:
            # Get provider handler
            provider = provider or request.GET.get('provider', 'sendgrid')

            # Verify webhook signature
            if not self.verify_webhook_signature(request, provider):
                logger.warning(f'Invalid webhook signature from {provider}')
                return Response(
                    {'error': 'Invalid signature'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Get handler for this provider
            handler = getattr(self, f'handle_{provider}', None)
            if not handler:
                return Response(
                    {'error': 'Unsupported email provider'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Process events
            events = handler(request.data)
            return Response({
                'status': 'success',
                'events_processed': len(events)
            })

        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def handle_sendgrid(self, data):
        """Process SendGrid webhook events"""
        events = []

        # Handle both array and single event
        event_list = data if isinstance(data, list) else [data]

        for event in event_list:
            try:
                event_type = event.get('event')
                tracking_id = event.get('tracking_id') or event.get('email_id')

                if not tracking_id:
                    continue

                # Map SendGrid event types to our system
                event_map = {
                    'processed': 'sent',
                    'delivered': 'delivered',
                    'open': 'opened',
                    'click': 'clicked',
                    'bounce': 'bounced',
                    'dropped': 'dropped',
                    'spamreport': 'spam',
                    'unsubscribe': 'unsubscribed'
                }

                mapped_type = event_map.get(event_type)
                if not mapped_type:
                    continue

                # Find and update email log
                email_log = EmailLog.objects.get(tracking_id=tracking_id)
                email_log.add_tracking_event(
                    event_type=mapped_type,
                    event_data=event
                )

                # Update email status if needed
                if mapped_type in ['delivered', 'bounced', 'dropped']:
                    email_log.status = mapped_type
                    email_log.save(update_fields=['status', 'updated_at'])

                events.append(mapped_type)

            except EmailLog.DoesNotExist:
                logger.warning(f"Email log not found for tracking_id: {tracking_id}")
            except Exception as e:
                logger.error(f"Error processing {event_type} event: {str(e)}")

        return events
```

### 9.4 Privacy & Compliance

#### 9.4.1 GDPR & Privacy Considerations

1. **IP Anonymization**
   ```python
   def anonymize_ip(ip_address):
       """Anonymize IP address by zeroing the last octet"""
       if not ip_address or ip_address == '127.0.0.1':
           return ip_address

       # Handle IPv4
       if '.' in ip_address:
           parts = ip_address.split('.')
           if len(parts) == 4:
               return f"{'.'.join(parts[:3])}.0"

       # Handle IPv6 (simplified)
       if ':' in ip_address:
           return ':'.join(ip_address.split(':')[:4] + ['0000'] * 4)

       return ip_address
   ```

2. **Data Retention**
   - Store raw IPs for security logs (14 days)
   - Anonymize IPs in tracking events after 30 days
   - Provide data export/deletion endpoints for compliance

3. **User Consent**
   - Add tracking preference in user/account settings
   - Include tracking info in email footers
   - Support one-click unsubscribe

### 9.5 Dashboard UI Implementation

#### 9.5.1 Frontend Components

1. **Email Analytics Dashboard**
   - Real-time delivery metrics
   - Interactive charts for open/click rates
   - Bounce and complaint tracking
   - Device/geography breakdowns

2. **Example Chart.js Implementation**
   ```html
   <div class="chart-container">
     <canvas id="emailMetricsChart"></canvas>
   </div>

   <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
   <script>
   // Fetch data from backend API
   fetch('/api/v1/analytics/emails/?days=30')
     .then(response => response.json())
     .then(data => {
       const ctx = document.getElementById('emailMetricsChart').getContext('2d');
       new Chart(ctx, {
         type: 'line',
         data: {
           labels: data.time_series.map(d => d.date),
           datasets: [{
             label: 'Open Rate %',
             data: data.time_series.map(d => d.open_rate),
             borderColor: 'rgb(75, 192, 192)',
             tension: 0.1
           }, {
             label: 'Click Rate %',
             data: data.time_series.map(d => d.click_through_rate),
             borderColor: 'rgb(54, 162, 235)',
             tension: 0.1
           }]
         },
         options: {
           responsive: true,
           plugins: {
             title: { display: true, text: 'Email Engagement (30 Days)' },
             tooltip: { mode: 'index', intersect: false },
             legend: { position: 'bottom' }
           },
           scales: {
             y: {
               min: 0,
               max: 100,
               ticks: { callback: value => `${value}%` }
             }
           }
         }
       });
     });
   </script>
   ```

3. **Responsive Design**
   - Mobile-first approach
   - Collapsible sections for smaller screens
   - Exportable reports (CSV/PDF)

### 9.6 Monitoring & Alerts

#### 9.4.1 Alert Conditions
```python
# monitoring/checks/email_health.py
def check_email_health():
    """Check for email delivery issues"""
    from datetime import timedelta
    from django.utils import timezone
    from ...models import EmailLog

    # Check for emails stuck in sending state
    threshold = timezone.now() - timedelta(hours=1)
    stuck_emails = EmailLog.objects.filter(
        status='sending',
        created_at__lt=threshold,
        is_processed=False
    )

    if stuck_emails.exists():
        send_alert(
            'high',
            f'{stuck_emails.count()} emails stuck in sending state',
            'Check Celery workers and SMTP configuration'
        )

    # Check for high bounce rate
    bounce_threshold = 5  # 5% bounce rate
    last_hour = timezone.now() - timedelta(hours=1)

    sent_count = EmailLog.objects.filter(created_at__gte=last_hour).count()
    bounced_count = EmailLog.objects.filter(
        created_at__gte=last_hour,
        status='bounced'
    ).count()

    if sent_count > 0:
        bounce_rate = (bounced_count / sent_count) * 100
        if bounce_rate > bounce_threshold:
            send_alert(
                'critical',
                f'High bounce rate: {bounce_rate:.1f}% in the last hour',
                'Check SMTP configuration and recipient email addresses'
            )
```

#### 9.4.2 Dashboard Metrics
```python
# v1/views/analytics.py
class EmailAnalyticsView(APIView):
    """API for email analytics and reporting"""

    def get(self, request, *args, **kwargs):
        store = getattr(request, 'store', None)
        days = int(request.query_params.get('days', 30))

        # Date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Base queryset
        logs = EmailLog.objects.filter(
            created_at__range=(start_date, end_date)
        )

        if store:
            logs = logs.filter(store=store)

        # Calculate metrics
        metrics = {
            'sent': logs.count(),
            'delivered': logs.filter(status='delivered').count(),
            'opened': logs.filter(tracking_events__event_type='opened')
                       .distinct().count(),
            'clicked': logs.filter(tracking_events__event_type='clicked')
                         .distinct().count(),
            'bounced': logs.filter(status='bounced').count(),
            'unsubscribed': logs.filter(tracking_events__event_type='unsubscribed')
                             .distinct().count(),
        }

        # Calculate rates
        metrics.update({
            'delivery_rate': self._safe_divide(metrics['delivered'], metrics['sent']) * 100,
            'open_rate': self._safe_divide(metrics['opened'], metrics['delivered']) * 100,
            'click_through_rate': self._safe_divide(metrics['clicked'], metrics['opened']) * 100,
            'bounce_rate': self._safe_divide(metrics['bounced'], metrics['sent']) * 100,
            'unsubscribe_rate': self._safe_divide(metrics['unsubscribed'], metrics['delivered']) * 100,
        })

        # Time series data
        time_series = self._get_time_series_data(logs, start_date, end_date)

        return Response({
            'metrics': metrics,
            'time_series': time_series,
            'period': {
                'start': start_date,
                'end': end_date
            }
        })

    def _safe_divide(self, numerator, denominator):
        """Safely divide two numbers, return 0 if denominator is 0"""
        return numerator / denominator if denominator else 0

    def _get_time_series_data(self, queryset, start_date, end_date):
        """Generate time series data for the given date range"""
        from django.db.models import Count, Q
        from django.db.models.functions import TruncDate

        # Group by date
        date_series = queryset.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            sent=Count('id'),
            delivered=Count('id', filter=Q(status='delivered')),
            opened=Count('tracking_events',
                       filter=Q(tracking_events__event_type='opened'),
                       distinct=True),
            clicked=Count('tracking_events',
                        filter=Q(tracking_events__event_type='clicked'),
                        distinct=True),
            bounced=Count('id', filter=Q(status='bounced')),
            unsubscribed=Count('tracking_events',
                             filter=Q(tracking_events__event_type='unsubscribed'),
                             distinct=True)
        ).order_by('date')

        # Convert to dict for easier lookup
        date_map = {item['date']: item for item in date_series}

        # Generate full date range
        result = []
        current_date = start_date.date()
        end_date = end_date.date()

        while current_date <= end_date:
            data = date_map.get(current_date, {
                'date': current_date,
                'sent': 0,
                'delivered': 0,
                'opened': 0,
                'clicked': 0,
                'bounced': 0,
                'unsubscribed': 0
            })

            # Calculate rates
            data.update({
                'delivery_rate': self._safe_divide(data['delivered'], data['sent']) * 100,
                'open_rate': self._safe_divide(data['opened'], data['delivered']) * 100,
                'click_through_rate': self._safe_divide(data['clicked'], data['opened']) * 100,
                'bounce_rate': self._safe_divide(data['bounced'], data['sent']) * 100,
                'unsubscribe_rate': self._safe_divide(data['unsubscribed'], data['delivered']) * 100,
            })

            result.append(data)
            current_date += timedelta(days=1)

        return result

### 9.1 Important Metrics
- Email delivery success/failure rates
- Average send time
- Queue size and processing time
- SMTP provider performance

### 9.2 Example Alerts
```python
# monitoring/checks/email_health.py
def check_email_queues():
    """Check for stuck email queues"""
    from datetime import timedelta
    from django.utils import timezone
    from ..models import EmailQueue

    # Check for emails stuck in queue for too long
    threshold = timezone.now() - timedelta(hours=1)
    stuck_emails = EmailQueue.objects.filter(
        is_processed=False,
        created_at__lt=threshold
    ).count()

    if stuck_emails > 10:
        send_alert(
            'high',
            f'{stuck_emails} emails stuck in queue',
            'Check Celery workers and SMTP configuration'
        )
```

## Review this final polished SMTP rules file carefully before applying.
