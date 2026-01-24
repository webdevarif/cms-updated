"""
Public API views for forms module.
"""
from django.http import StreamingHttpResponse
from rest_framework import viewsets, status, mixins, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from drf_spectacular.utils import extend_schema

from ..models.forms import FormTemplate
from ..models.submissions import FormSubmission, FormSubmissionData
from .serializers import FormTemplateSerializer, FormSubmissionSerializer
from ..services import FormService


class FormRateThrottle(UserRateThrottle):
    scope = 'forms'


class PublicFormViewSet(viewsets.ModelViewSet):
    """
    Public form endpoints
    - List/retrieve published + active forms
    - Submit via form_id
    """

    permission_classes = [AllowAny]
    throttle_classes = [FormRateThrottle, AnonRateThrottle]
    serializer_class = FormTemplateSerializer
    queryset = FormTemplate.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'slug', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(store=self.request.store, status='published', is_active=True)

    def get_object(self):
        """Lookup by form_id for public routes."""
        form_id = self.kwargs.get('pk')
        if form_id:
            from django.shortcuts import get_object_or_404
            return get_object_or_404(self.get_queryset(), form_id=form_id)
        return super().get_object()

    @extend_schema(
        summary="List published forms",
        description="List all published and active forms for the current store",
        responses={200: FormTemplateSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List published forms"""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Get form by ID",
        description="Retrieve a published form by its form_id",
        responses={200: FormTemplateSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        """Get form by form_id"""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Submit form",
        description="Submit form data using form_id",
        request=FormSubmissionSerializer,
        responses={201: dict}
    )
    @action(detail=True, methods=['post'], url_path='submit')
    def submit_form(self, request, pk=None):
        """Submit form data"""
        form = self.get_object()
        
        # Add request metadata
        submission_data = request.data.copy()
        submission_data.update({
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'form_data': request.data
        })
        
        # Process submission using service
        result = FormService.process_submission(
            store=request.store,
            form=form,
            data=submission_data,
            user=request.user if request.user.is_authenticated else None
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @extend_schema(
        summary="Get form submissions",
        description="Get all submissions for a form (admin only)",
        responses={200: dict}
    )
    @action(detail=True, methods=['get'], url_path='submissions')
    def get_submissions(self, request, pk=None):
        """Get form submissions"""
        form = self.get_object()
        
        # Check if user has permission to view submissions
        if not self.has_submission_permission(request, form):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        result = FormService.get_form_submissions(
            store=request.store,
            form_id=form.id
        )
        
        if result:
            serializer = FormSubmissionSerializer(result['submissions'], many=True)
            return Response({
                'form': FormTemplateSerializer(form).data,
                'submissions': serializer.data,
                'count': result['count']
            })
        
        return Response({'error': 'Form not found'}, status=status.HTTP_404_NOT_FOUND)

    def has_submission_permission(self, request, form):
        """Check if user has permission to view submissions"""
        # Allow if user is authenticated and is store admin or form creator
        if request.user.is_authenticated:
            if hasattr(request.user, 'store_memberships'):
                membership = request.user.store_memberships.filter(
                    store=request.store,
                    role__in=['admin', 'owner']
                ).first()
                if membership:
                    return True
        return False


class CustomerFormViewSet(PublicFormViewSet):
    """
    Customer form endpoints with authentication
    """
    from rest_framework.permissions import IsAuthenticated
    from core.permissions import IsStoreUser
    
    permission_classes = [IsAuthenticated, IsStoreUser]
    
    @extend_schema(
        summary="Create form",
        description="Create a new form template",
        request=FormTemplateSerializer,
        responses={201: FormTemplateSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Create a new form"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        form = FormService.create_form(
            store=request.store,
            user=request.user,
            data=serializer.validated_data
        )
        
        return Response(
            FormTemplateSerializer(form).data,
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        summary="Update form",
        description="Update an existing form",
        request=FormTemplateSerializer,
        responses={200: FormTemplateSerializer}
    )
    def update(self, request, *args, **kwargs):
        """Update form"""
        form = self.get_object()
        
        # Update form fields
        for field, value in request.data.items():
            if hasattr(form, field):
                setattr(form, field, value)
        
        form.save()
        
        return Response(
            FormTemplateSerializer(form).data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Delete form",
        description="Delete a form template",
        responses={204: None}
    )
    def destroy(self, request, *args, **kwargs):
        """Delete form"""
        form = self.get_object()
        form.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DashboardFormViewSet(CustomerFormViewSet):
    """
    Dashboard form endpoints with admin permissions
    """
    from rest_framework.permissions import IsAuthenticated
    from core.permissions import IsStoreAdmin
    
    permission_classes = [IsAuthenticated, IsStoreAdmin]
    
    @extend_schema(
        summary="Export form submissions",
        description="Export form submissions to CSV",
        responses={200: 'text/csv'}
    )
    @action(detail=True, methods=['get'], url_path='export')
    def export_submissions(self, request, pk=None):
        """Export form submissions to CSV"""
        form = self.get_object()
        
        result = FormService.get_form_submissions(
            store=request.store,
            form_id=form.id
        )
        
        if not result:
            return Response({'error': 'No submissions found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create CSV response
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="form_{form.form_id}_submissions.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow(['Submission ID', 'Date', 'User', 'Email', 'Form Data'])
        
        # Write data
        for submission in result['submissions']:
            writer.writerow([
                submission.id,
                submission.created_at,
                submission.user.email if submission.user else 'Anonymous',
                submission.ip_address,
                submission.get_form_data_as_dict()
            ])
        
        return response
