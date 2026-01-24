"""
Views for email management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from ..models import EmailLog
from ..serializers import EmailLogSerializer


class EmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Email log viewset"""
    serializer_class = EmailLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return EmailLog.objects.filter(store=self.request.store)
    
    @extend_schema(
        summary="List email logs",
        description="List sent emails with filtering",
        responses={200: list}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get email log",
        description="Get a specific email log",
        responses={200: dict}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
