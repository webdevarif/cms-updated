"""
Views for email template management.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from ..models import EmailTemplate
from ..serializers import EmailTemplateSerializer


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """Email template management"""
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return EmailTemplate.objects.filter(store=self.request.store)
    
    def perform_create(self, serializer):
        serializer.save(store=self.request.store)
    
    @extend_schema(
        summary="List email templates",
        description="List email templates for the store",
        responses={200: list}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get email template",
        description="Get a specific email template",
        responses={200: dict}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
