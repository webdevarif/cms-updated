"""
Common choice enumerations for Digital Farmers CMS.
"""

from django.utils.translation import gettext_lazy as _


class StatusChoices:
    """Common status choices"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"
    PENDING = "pending"
    PUBLISHED = "published"

    CHOICES = [
        (ACTIVE, _("Active")),
        (INACTIVE, _("Inactive")),
        (DRAFT, _("Draft")),
        (ARCHIVED, _("Archived")),
        (PENDING, _("Pending")),
        (PUBLISHED, _("Published")),
    ]


class OrderStatusChoices:
    """Order status choices"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"

    CHOICES = [
        (PENDING, _("Pending")),
        (CONFIRMED, _("Confirmed")),
        (PROCESSING, _("Processing")),
        (SHIPPED, _("Shipped")),
        (DELIVERED, _("Delivered")),
        (CANCELLED, _("Cancelled")),
        (REFUNDED, _("Refunded")),
        (PARTIALLY_REFUNDED, _("Partially Refunded")),
    ]


class PaymentStatusChoices:
    """Payment status choices"""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"

    CHOICES = [
        (PENDING, _("Pending")),
        (COMPLETED, _("Completed")),
        (FAILED, _("Failed")),
        (REFUNDED, _("Refunded")),
        (PARTIALLY_REFUNDED, _("Partially Refunded")),
    ]


class ProductStatusChoices:
    """Product status choices"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"
    OUT_OF_STOCK = "out_of_stock"

    CHOICES = [
        (ACTIVE, _("Active")),
        (INACTIVE, _("Inactive")),
        (DRAFT, _("Draft")),
        (ARCHIVED, _("Archived")),
        (OUT_OF_STOCK, _("Out of Stock")),
    ]


class UserStatusChoices:
    """User status choices"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"

    CHOICES = [
        (ACTIVE, _("Active")),
        (INACTIVE, _("Inactive")),
        (PENDING, _("Pending")),
        (SUSPENDED, _("Suspended")),
    ]


class NotificationChannelChoices:
    """Notification channel choices"""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"

    CHOICES = [
        (EMAIL, _("Email")),
        (SMS, _("SMS")),
        (PUSH, _("Push")),
        (IN_APP, _("In-App")),
    ]


class ContentTypeChoices:
    """Content type choices"""

    TEXT = "text"
    HTML = "html"
    JSON = "json"
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"

    CHOICES = [
        (TEXT, _("Text")),
        (HTML, _("HTML")),
        (JSON, _("JSON")),
        (IMAGE, _("Image")),
        (VIDEO, _("Video")),
        (DOCUMENT, _("Document")),
    ]


class PriorityChoices:
    """Priority choices"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

    CHOICES = [
        (LOW, _("Low")),
        (MEDIUM, _("Medium")),
        (HIGH, _("High")),
        (URGENT, _("Urgent")),
    ]


class FrequencyChoices:
    """Frequency choices"""

    IMMEDIATELY = "immediately"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

    CHOICES = [
        (IMMEDIATELY, _("Immediately")),
        (HOURLY, _("Hourly")),
        (DAILY, _("Daily")),
        (WEEKLY, _("Weekly")),
        (MONTHLY, _("Monthly")),
    ]


class YesNoChoices:
    """Yes/No choices"""

    YES = "yes"
    NO = "no"

    CHOICES = [
        (YES, _("Yes")),
        (NO, _("No")),
    ]


class BooleanChoices:
    """Boolean choices"""

    TRUE = "true"
    FALSE = "false"

    CHOICES = [
        (TRUE, _("True")),
        (FALSE, _("False")),
    ]
