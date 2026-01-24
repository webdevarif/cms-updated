"""
Customer Forms API v2

Provides form management for store customers with appropriate permissions.
"""
from django.db import transaction
from django.http import Http404
from django_filters import rest_framework as filters
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter

from core.permissions import IsStoreCustomer
from apps.public.forms.models.forms import FormTemplate, FormSubmission, EmailTemplate
from apps.public.forms.services import FormService
from . import serializers as customer_serializers


class CustomerFormFilter(filters.FilterSet):
    """Filters for customer form templates"""
    status = filters.ChoiceFilter(choices=FormTemplate.STATUS_CHOICES)
    is_active = filters.BooleanFilter()
    search = filters.CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = FormTemplate
        fields = ['status', 'is_active', 'search']


class CustomerFormSubmissionFilter(filters.FilterSet):
    """Filters for form submissions"""
    status = filters.ChoiceFilter(choices=FormSubmission.STATUS_CHOICES)
    email_sent = filters.BooleanFilter()
    email_opened = filters.BooleanFilter()
    date_from = filters.DateFilter(field_name='submitted_at', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='submitted_at', lookup_expr='lte')

    class Meta:
        model = FormSubmission
        fields = ['status', 'email_sent', 'email_opened', 'date_from', 'date_to']


class CustomerFormViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    Customer Forms API
    
    Provides form management for store customers with appropriate permissions.
    """
    permission_classes = [IsAuthenticated, IsStoreCustomer]
    serializer_class = customer_serializers.CustomerFormTemplateSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = CustomerFormFilter
    
    def get_queryset(self):
        """Return forms for the current store"""
        return FormTemplate.objects.filter(
            store=self.request.store,
            is_active=True  # Only show active forms by default
        ).select_related('store').prefetch_related('submissions')
    
    def perform_create(self, serializer):
        """Set the store and generate form_id"""
        instance = serializer.save(store=self.request.store)
        # Generate form_id if not provided
        if not instance.form_id:
            instance.form_id = FormTemplate.generate_form_id()
            instance.save(update_fields=['form_id'])
    
    def perform_update(self, serializer):
        """Ensure store cannot be changed"""
        serializer.save(store=self.request.store)
    
    @extend_schema(
        summary="List Forms",
        description="List all forms for the current store",
        responses={200: customer_serializers.CustomerFormTemplateSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Form",
        description="Create a new form template",
        responses={201: customer_serializers.CustomerFormTemplateSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get Form",
        description="Retrieve a form template by ID",
        responses={200: customer_serializers.CustomerFormTemplateSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Form",
        description="Update a form template",
        responses={200: customer_serializers.CustomerFormTemplateSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Form",
        description="Delete a form template",
        responses={204: None}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @extend_schema(
        summary="Publish Form",
        description="Publish a draft form",
        methods=['POST'],
        responses={
            200: customer_serializers.CustomerFormTemplateSerializer,
            400: "Form is not in draft status"
        }
    )
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        form = self.get_object()
        if form.status != 'draft':
            return Response(
                {'error': 'Only draft forms can be published'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        form.status = 'published'
        form.save(update_fields=['status', 'updated_at'])
        serializer = self.get_serializer(form)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Archive Form",
        description="Archive a published form",
        methods=['POST'],
        responses={
            200: customer_serializers.CustomerFormTemplateSerializer,
            400: "Only published forms can be archived"
        }
    )
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        form = self.get_object()
        if form.status != 'published':
            return Response(
                {'error': 'Only published forms can be archived'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        form.status = 'archived'
        form.save(update_fields=['status', 'updated_at'])
        serializer = self.get_serializer(form)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Duplicate Form",
        description="Create a duplicate of an existing form",
        methods=['POST'],
        responses={
            201: customer_serializers.CustomerFormTemplateSerializer,
            400: "Form not found or inaccessible"
        }
    )
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        try:
            original = self.get_queryset().get(pk=pk)
        except FormTemplate.DoesNotExist:
            raise Http404("Form not found or you don't have permission to access it")
        
        try:
            duplicate = FormService.duplicate_form(original)
            serializer = self.get_serializer(duplicate)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="List Form Submissions",
        description="List all submissions for a form",
        parameters=[
            OpenApiParameter(
                name='status',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Filter by submission status',
                enum=[s[0] for s in FormSubmission.STATUS_CHOICES]
            ),
            OpenApiParameter(
                name='email_sent',
                type=bool,
                location=OpenApiParameter.QUERY,
                description='Filter by email sent status'
            ),
            OpenApiParameter(
                name='date_from',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Filter submissions from this date (YYYY-MM-DD)'
            ),
            OpenApiParameter(
                name='date_to',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Filter submissions to this date (YYYY-MM-DD)'
            ),
        ],
        responses={
            200: customer_serializers.CustomerFormSubmissionSerializer(many=True),
            404: "Form not found"
        }
    )
    @action(detail=True, methods=['get'], url_path='submissions')
    def submissions(self, request, pk=None):
        form = self.get_object()
        queryset = form.submissions.all()
        
        # Apply filters
        filterset = CustomerFormSubmissionFilter(request.query_params, queryset=queryset)
        filtered_queryset = filterset.qs
        
        # Paginate results
        page = self.paginate_queryset(filtered_queryset)
        if page is not None:
            serializer = customer_serializers.CustomerFormSubmissionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = customer_serializers.CustomerFormSubmissionSerializer(filtered_queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Export Submissions",
        description="Export form submissions as CSV",
        responses={
            200: "CSV file with submissions data",
            404: "Form not found"
        }
    )
    @action(detail=True, methods=['get'], url_path='export')
    def export_submissions(self, request, pk=None):
        import csv
        from django.http import StreamingHttpResponse
        
        form = self.get_object()
        queryset = form.submissions.all()
        
        # Apply filters
        filterset = CustomerFormSubmissionFilter(request.query_params, queryset=queryset)
        filtered_queryset = filterset.qs
        
        # Define CSV headers and field mappings
        field_names = [
            'id', 'submitted_at', 'status', 'email_sent', 'email_opened',
            'ip_address', 'user_agent', 'data'
        ]
        
        class Echo:
            """Helper class to stream CSV data"""
            def write(self, value):
                return value
        
        def generate_csv():
            """Generator to stream CSV data"""
            writer = csv.DictWriter(Echo(), fieldnames=field_names)
            
            # Write header
            yield writer.writerow(dict(zip(field_names, field_names)))
            
            # Write rows
            for submission in filtered_queryset.iterator():
                row = {
                    'id': submission.id,
                    'submitted_at': submission.submitted_at.isoformat(),
                    'status': submission.status,
                    'email_sent': 'Yes' if submission.email_sent else 'No',
                    'email_opened': 'Yes' if submission.email_opened else 'No',
                    'ip_address': submission.ip_address or '',
                    'user_agent': submission.user_agent or '',
                    'data': str(submission.data)  # Convert dict to string
                }
                yield writer.writerow(row)
        
        # Create streaming response
        response = StreamingHttpResponse(
            generate_csv(),
            content_type='text/csv'
        )
        response['Content-Disposition'] = f'attachment; filename="form_{form.id}_submissions.csv"'
        return response


class CustomerEmailTemplateViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    Customer Email Templates API
    
    Provides email template management for form notifications.
    """
    permission_classes = [IsAuthenticated, IsStoreCustomer]
    serializer_class = customer_serializers.CustomerEmailTemplateSerializer
    
    def get_queryset(self):
        """Return email templates for the current store"""
        return EmailTemplate.objects.filter(
            store=self.request.store
        )
    
    def perform_create(self, serializer):
        """Set the store"""
        serializer.save(store=self.request.store)
    
    def perform_update(self, serializer):
        """Ensure store cannot be changed"""
        serializer.save(store=self.request.store)
    
    @extend_schema(
        summary="List Email Templates",
        description="List all email templates for the current store",
        responses={200: customer_serializers.CustomerEmailTemplateSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Email Template",
        description="Create a new email template",
        responses={201: customer_serializers.CustomerEmailTemplateSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get Email Template",
        description="Retrieve an email template by ID",
        responses={200: customer_serializers.CustomerEmailTemplateSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Email Template",
        description="Update an email template",
        responses={200: customer_serializers.CustomerEmailTemplateSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Email Template",
        description="Delete an email template",
        responses={204: None}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
