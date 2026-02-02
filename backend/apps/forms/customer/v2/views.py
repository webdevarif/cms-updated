"""
Customer Forms API v2

Provides form management for store customers with appropriate permissions.
"""

from apps.forms.models import FormSubmission, FormTemplate
from apps.forms.services import FormService
from core.permissions import IsStoreUser
from django.db import transaction
from django.http import Http404
from django_filters import rest_framework as filters
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import CustomerFormSubmissionSerializer, CustomerFormTemplateSerializer


class CustomerFormFilter(filters.FilterSet):
    """Filters for customer form templates"""

    status = filters.ChoiceFilter(
        choices=[
            ("draft", "Draft"),
            ("published", "Published"),
            ("archived", "Archived"),
        ]
    )
    is_active = filters.BooleanFilter()
    search = filters.CharFilter(field_name="title", lookup_expr="icontains")

    class Meta:
        model = FormTemplate
        fields = ["status", "is_active", "search"]


class CustomerFormViewSet(viewsets.ModelViewSet):
    """
    Customer form management endpoints.
    - CRUD operations on form templates
    - View and manage submissions
    - Email template management
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = CustomerFormTemplateSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = CustomerFormFilter

    def get_queryset(self):
        """Filter forms by current user's store"""
        return FormTemplate.objects.filter(store=self.request.store)

    @extend_schema(
        summary="Get form submissions",
        description="Get all submissions for a form",
        parameters=[
            OpenApiParameter(
                name="status",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter by submission status",
            )
        ],
    )
    @action(detail=True, methods=["get"])
    def submissions(self, request, pk=None):
        """Get form submissions"""
        form = self.get_object()
        submissions = form.submissions.all()

        status_filter = request.query_params.get("status")
        if status_filter:
            submissions = submissions.filter(status=status_filter)

        serializer = CustomerFormSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Duplicate form",
        description="Create a copy of an existing form",
        responses={201: CustomerFormTemplateSerializer},
    )
    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        """Duplicate a form template"""
        form = self.get_object()

        with transaction.atomic():
            new_form = FormService.duplicate_form(
                form=form,
                new_title=request.data.get("title", f"{form.title} (Copy)"),
                user=request.user,
            )

        serializer = self.get_serializer(new_form)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Toggle form status", description="Enable or disable a form")
    @action(detail=True, methods=["post"])
    def toggle_status(self, request, pk=None):
        """Toggle form active status"""
        form = self.get_object()
        form.is_active = not form.is_active
        form.save()

        return Response(
            {
                "is_active": form.is_active,
                "message": f'Form {"activated" if form.is_active else "deactivated"}',
            }
        )
