"""
Custom validators for Digital Farmers CMS.
"""

import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_phone_number(value):
    """
    Validate phone number format.
    Examples: +1234567890, (123) 456-7890, 123-456-7890, 123.456.7890
    """
    pattern = r"^\+?1?[-. (]*\d{3}[-. )]*\d{3}[-. ]*\d{4}$"
    if not re.match(pattern, value):
        raise ValidationError(_("Enter a valid phone number."), code="invalid_phone")


def validate_zip_code(value):
    """Validate US ZIP code format"""
    pattern = r"^\d{5}(?:[-\s]?\d{4})?$"
    if not re.match(pattern, value):
        raise ValidationError(_("Enter a valid ZIP code."), code="invalid_zip")


def validate_strong_password(value):
    """
    Validate that a password is strong.
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """
    if len(value) < 8:
        raise ValidationError(
            _("Password must be at least 8 characters long."), code="password_too_short"
        )

    if not any(c.isupper() for c in value):
        raise ValidationError(
            _("Password must contain at least one uppercase letter."),
            code="password_no_upper",
        )

    if not any(c.islower() for c in value):
        raise ValidationError(
            _("Password must contain at least one lowercase letter."),
            code="password_no_lower",
        )

    if not any(c.isdigit() for c in value):
        raise ValidationError(
            _("Password must contain at least one number."), code="password_no_digit"
        )

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError(
            _("Password must contain at least one special character."),
            code="password_no_special",
        )


def validate_url(value):
    """Validate URL format"""
    url_pattern = re.compile(
        r"^(https?://)"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    if not url_pattern.match(value):
        raise ValidationError(_("Enter a valid URL."), code="invalid_url")


def validate_color_hex(value):
    """Validate hex color code"""
    pattern = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    if not re.match(pattern, value):
        raise ValidationError(_("Enter a valid hex color code."), code="invalid_color")


def validate_domain(value):
    """Validate domain name"""
    pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    if not re.match(pattern, value):
        raise ValidationError(_("Enter a valid domain name."), code="invalid_domain")


def validate_file_extension(value, allowed_extensions):
    """
    Validate file extension against allowed extensions.

    Args:
        value: File object or filename string
        allowed_extensions: List of allowed extensions (without dot)
    """
    if hasattr(value, "name"):
        filename = value.name
    else:
        filename = value

    extension = filename.split(".")[-1].lower() if "." in filename else ""

    if extension not in allowed_extensions:
        raise ValidationError(
            _("File extension not allowed. Allowed extensions: %(allowed)s.")
            % {"allowed": ", ".join(allowed_extensions)},
            code="invalid_extension",
        )


def validate_image_size(value):
    """Validate image file size"""
    max_size = getattr(settings, "MAX_IMAGE_SIZE_MB", 10)

    if hasattr(value, "size"):
        size_mb = value.size / (1024 * 1024)
        if size_mb > max_size:
            raise ValidationError(
                _("Image size cannot exceed %(max_size)sMB.") % {"max_size": max_size},
                code="image_too_large",
            )


def validate_positive_number(value):
    """Validate that value is a positive number"""
    try:
        num_value = float(value)
        if num_value <= 0:
            raise ValidationError(_("Value must be a positive number."), code="not_positive")
    except (ValueError, TypeError):
        raise ValidationError(_("Enter a valid number."), code="invalid_number")


def validate_future_date(value):
    """Validate that date is in the future"""
    from django.utils import timezone

    if value <= timezone.now().date():
        raise ValidationError(_("Date must be in the future."), code="past_date")


def validate_slug(value):
    """Validate slug format"""
    pattern = r"^[-a-zA-Z0-9_]+$"
    if not re.match(pattern, value):
        raise ValidationError(
            _("Enter a valid slug consisting of letters, numbers, hyphens, and underscores only."),
            code="invalid_slug",
        )
