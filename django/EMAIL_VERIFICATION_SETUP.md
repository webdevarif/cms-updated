# Email Verification Setup Guide

## Overview
This application supports email verification for user registration. The system can be configured for development (console backend) or production (SMTP backend).

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Email Configuration
# For development (emails printed to console)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# For production (SMTP)
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Email Verification Settings
# Set to False for development, True for production
EMAIL_VERIFICATION_ENABLED=False
```

### Email Templates

Custom email templates are located at:
- `apps/accounts/templates/account/email/email_confirmation_message.txt`
- `apps/accounts/templates/account/email/email_confirmation_subject.txt`
- `apps/accounts/templates/account/email/password_reset_message.txt`
- `apps/accounts/templates/account/email/password_reset_subject.txt`

## Development Setup

1. **Console Backend** (Default):
   - Emails are printed to the console
   - No SMTP configuration needed
   - Set `EMAIL_VERIFICATION_ENABLED=False` to skip verification

2. **Testing Email Verification**:
   ```bash
   # Enable verification for testing
   EMAIL_VERIFICATION_ENABLED=True

   # Register a new user
   POST /auth/users/
   {
     "email": "test@example.com",
     "username": "testuser",
     "password": "testpass123",
     "re_password": "testpass123"
   }

   # Check console for activation email
   # Copy the activation URL and visit it
   ```

## Production Setup

1. **SMTP Configuration**:
   ```bash
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_VERIFICATION_ENABLED=True
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password
   DEFAULT_FROM_EMAIL=noreply@yourdomain.com
   ```

2. **Gmail Setup**:
   - Enable 2-factor authentication on your Gmail account
   - Generate an App Password: Google Account → Security → App Passwords
   - Use the App Password as `EMAIL_HOST_PASSWORD`

## Email Verification Flow

1. **User Registration**:
   - User registers via `/auth/users/`
   - Account created as inactive
   - Verification email sent

2. **Email Verification**:
   - User clicks verification link
   - Account activated
   - User can now login

3. **Login Attempt**:
   - Unverified users cannot login
   - Returns: "No active account found with the given credentials"

## API Endpoints

### Registration
```http
POST /auth/users/
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "re_password": "password123",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Login (after verification)
```http
POST /auth/jwt/create/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

### Resend Activation
```http
POST /auth/users/resend_activation/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

## Troubleshooting

### Common Issues

1. **Email not sending**:
   - Check SMTP credentials
   - Verify App Password for Gmail
   - Check firewall/port settings

2. **Verification link not working**:
   - Check `ACTIVATION_URL` configuration
   - Verify frontend URL mapping

3. **User can't login after verification**:
   - Check if user is actually activated
   - Verify email/username authentication backend

### Debug Mode

For debugging email issues:
```python
# In settings.py
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

This will print all emails to the console for inspection.

## Security Considerations

1. **Email Verification**: Always enabled in production
2. **Password Reset**: Secure token-based reset
3. **Rate Limiting**: Prevent email spam
4. **Secure SMTP**: Use TLS and strong passwords

## Testing

Use the console backend to test email templates and flow without sending real emails:

```bash
# Set in .env
EMAIL_VERIFICATION_ENABLED=True
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Then register a user and check the console output for the verification email.
