"""
Dashboard Forms API Views

This module provides form management functionality for store administrators.
"""
from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend

from core.permissions import IsStoreOwner
from apps.forms.models import FormTemplate, FormSubmission
from apps.forms.services import FormService
from .serializers import (
    DashboardFormTemplateSerializer, 
    DashboardFormSubmissionSerializer
)


class DashboardFormTemplateViewSet(viewsets.ModelViewSet):
    """Dashboard viewset for form templates with admin access"""
    
    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = DashboardFormTemplateSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'title']
    
    def get_queryset(self):
        """Filter forms by current user's store"""
        return FormTemplate.objects.filter(store=self.request.store)

    @extend_schema(
        summary="Get form analytics",
        description="Get analytics data for a form"
    )
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get form analytics"""
        form = self.get_object()
        analytics = FormService.get_form_analytics(form)
        return Response(analytics)

    @extend_schema(
        summary="Export form data",
        description="Export form submissions and configuration"
    )
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """Export form data"""
        form = self.get_object()
        export_data = FormService.export_form_data(form)
        return Response(export_data)

    @extend_schema(
        summary="Import form data",
        description="Import form configuration from export data"
    )
    @action(detail=False, methods=['post'])
    def import_form(self, request):
        """Import form from export data"""
        imported_form = FormService.import_form_data(
            store=request.store,
            data=request.data,
            user=request.user
        )
        serializer = self.get_serializer(imported_form)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DashboardFormSubmissionViewSet(viewsets.ModelViewSet):
    """Dashboard viewset for form submissions with admin access"""
    
    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = DashboardFormSubmissionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'form_template', 'submitted_at']
    search_fields = ['user__username', 'user__email']
    ordering_fields = ['submitted_at', 'processed_at']
    
    def get_queryset(self):
        """Filter submissions by current user's store"""
        return FormSubmission.objects.filter(form_template__store=self.request.store)

    @extend_schema(
        summary="Update submission status",
        description="Update the status of a form submission"
    )
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update submission status"""
        submission = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in ['pending', 'processing', 'completed', 'failed']:
            return Response(
                {"error": "Invalid status"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        submission.status = new_status
        submission.save()
        
        serializer = self.get_serializer(submission)
        return Response(serializer.data)

    @extend_schema(
        summary="Bulk update submissions",
        description="Update multiple submissions at once"
    )
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update submissions"""
        submission_ids = request.data.get('submission_ids', [])
        updates = request.data.get('updates', {})
        
        updated_count = FormService.bulk_update_submissions(
            submission_ids=submission_ids,
            updates=updates,
            store=request.store
        )
        
        return Response({"updated_count": updated_count})
