"""
Customer SMTP email views.
"""

from apps.smtp.models import EmailLog
from core.permissions import IsStoreUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from .serializers import EmailLogCustomerSerializer


class EmailLogCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Customer email log endpoints.
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = EmailLogCustomerSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["to_email", "subject", "status"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    filterset_fields = ["status", "smtp_config"]

    def get_queryset(self):
        """Filter email logs by current user's store"""
        return EmailLog.objects.filter(smtp_config__store=self.request.store).select_related(
            "smtp_config"
        )
