"""
General utilities for Digital Farmers CMS.
"""
import hashlib
import json
import logging
import re
import uuid
from datetime import datetime, timedelta

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.text import slugify

logger = logging.getLogger(__name__)


def generate_unique_id(length=8):
    """
    Generate a unique ID for models.
    """
    return uuid.uuid4().hex[:length].upper()


def generate_unique_slug(model_class, text, instance=None):
    """
    Generate unique slug for a model.
    """
    slug = slugify(text)
    original_slug = slug
    counter = 1

    while True:
        queryset = model_class.objects.filter(slug=slug)
        if instance:
            queryset = queryset.exclude(pk=instance.pk)

        if not queryset.exists():
            break

        slug = f"{original_slug}-{counter}"
        counter += 1

    return slug


def clean_filename(filename):
    """
    Clean filename for safe storage.
    """
    # Remove special characters
    filename = re.sub(r"[^\w\s.-]", "", filename)
    # Replace spaces with underscores
    filename = re.sub(r"\s+", "_", filename)
    # Convert to lowercase
    filename = filename.lower()
    return filename


def get_client_ip(request):
    """
    Get client IP address from request.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def validate_file_size(file, max_size_mb):
    """
    Validate file size.
    """
    if isinstance(file, InMemoryUploadedFile):
        size_mb = file.size / (1024 * 1024)
        if size_mb > max_size_mb:
            raise ValueError(f"File size {size_mb:.2f}MB exceeds maximum {max_size_mb}MB")
    return True


def generate_hash(text, salt=None):
    """
    Generate SHA256 hash of text with optional salt.
    """
    if salt is None:
        salt = settings.SECRET_KEY

    combined = f"{text}{salt}"
    return hashlib.sha256(combined.encode()).hexdigest()


def format_currency(amount, currency="USD"):
    """
    Format currency amount.
    """
    try:
        if currency == "USD":
            return f"${amount:,.2f}"
        elif currency == "EUR":
            return f"€{amount:,.2f}"
        elif currency == "GBP":
            return f"£{amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"
    except (ValueError, TypeError):
        return f"{amount:,.2f}"


def truncate_text(text, max_length=100, suffix="..."):
    """
    Truncate text to specified length.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def parse_date_range(date_string):
    """
    Parse date range string and return start/end dates.
    """
    if not date_string:
        return None, None

    try:
        if " to " in date_string:
            start_str, end_str = date_string.split(" to ")
            start_date = datetime.strptime(start_str.strip(), "%Y-%m-%d")
            end_date = datetime.strptime(end_str.strip(), "%Y-%m-%d")
        else:
            # Single date
            start_date = datetime.strptime(date_string.strip(), "%Y-%m-%d")
            end_date = start_date + timedelta(days=1)

        return start_date, end_date
    except ValueError:
        return None, None


def sanitize_filename(filename):
    """
    Sanitize filename for safe storage.
    """
    # Remove path separators
    filename = filename.replace("/", "_").replace("\\", "_")
    # Remove control characters
    filename = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", filename)
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[: 255 - len(ext) - 1] + "." + ext if ext else name[:255]
    return filename


def is_valid_json(text):
    """
    Check if text is valid JSON.
    """
    try:
        json.loads(text)
        return True
    except (ValueError, TypeError):
        return False


def get_file_extension(filename):
    """
    Get file extension from filename.
    """
    return filename.split(".")[-1].lower() if "." in filename else ""


def format_bytes(bytes_value):
    """
    Format bytes into human readable format.
    """
    if bytes_value < 1024:
        return f"{bytes_value} B"
    elif bytes_value < 1024 * 1024:
        return f"{bytes_value / 1024:.1f} KB"
    elif bytes_value < 1024 * 1024 * 1024:
        return f"{bytes_value / (1024 * 1024):.1f} MB"
    else:
        return f"{bytes_value / (1024 * 1024 * 1024):.1f} GB"
