from core.models import TenantModel

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class EventLog(TenantModel):
    EVENT_TYPES = [
        ("SEARCH_QUERY", "Search Query"),
        ("SEARCH_RESULTS", "Search Results"),
        ("PAGE_VIEW", "Page View"),
        ("CONTENT_VIEW", "Content View"),
        ("CONTENT_ACTION", "Content Action"),
        ("USER_ACTION", "User Action"),
        ("USER_AUTH", "User Authentication"),
        ("SYSTEM_EVENT", "System Event"),
        ("SECURITY_EVENT", "Security Event"),
        ("SALE_EVENT", "Sale Event"),
        ("FORM_SUBMIT", "Form Submit"),
    ]
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    event_name = models.CharField(max_length=255)
    properties = models.JSONField(default=dict)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    session_id = models.UUIDField(null=True)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    request_id = models.CharField(max_length=100, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["store", "event_type", "created_at"]),
            models.Index(fields=["store", "created_at"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["session_id"]),
            models.Index(fields=["event_name"]),
        ]
        ordering = ["-created_at"]


class SearchLog(TenantModel):
    query = models.CharField(max_length=255, db_index=True)
    results_count = models.PositiveIntegerField(default=0)
    success = models.BooleanField(default=True)
    search_type = models.CharField(max_length=50, default="content")
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    session_id = models.UUIDField(null=True)
    ip_address = models.GenericIPAddressField(null=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["store", "query", "created_at"]),
            models.Index(fields=["store", "created_at"]),
        ]
        ordering = ["-created_at"]
