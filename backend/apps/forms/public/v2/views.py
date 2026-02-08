"""
Public API views for forms module.
"""

from apps.forms.models import FormSubmission, FormTemplate
from apps.forms.services import FormService
from drf_spectacular.utils import extend_schema
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from django.http import StreamingHttpResponse

from .serializers import FormSubmissionSerializer, FormTemplateSerializer


class FormRateThrottle(UserRateThrottle):
    scope = "forms"


class PublicFormViewSet(viewsets.ModelViewSet):
    """
    Public form endpoints
    - List/retrieve published + active forms
    - Submit via form_id
    """

    permission_classes = [AllowAny]
    throttle_classes = [FormRateThrottle, AnonRateThrottle]
    serializer_class = FormTemplateSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "title"]

    def get_queryset(self):
        """Only return published and active forms"""
        return FormTemplate.objects.filter(status="published", is_active=True).select_related(
            "store"
        )

    @extend_schema(
        summary="Submit form",
        description="Submit a form with data",
        request=FormSubmissionSerializer,
        responses={201: FormSubmissionSerializer},
    )
    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """Submit form data"""
        form = self.get_object()

        # Validate form is accepting submissions
        if not form.is_accepting_submissions:
            return Response(
                {"error": "Form is not accepting submissions"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = FormSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        submission = FormService.create_submission(
            form=form, data=serializer.validated_data, request=request
        )

        return Response(FormSubmissionSerializer(submission).data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Download submissions", description="Download form submissions as CSV")
    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """Download form submissions as CSV"""
        form = self.get_object()

        # Check if form allows public downloads
        if not form.allow_public_downloads:
            return Response(
                {"error": "Public downloads not allowed"},
                status=status.HTTP_403_FORBIDDEN,
            )

        csv_content = FormService.generate_submissions_csv(form)
        response = StreamingHttpResponse(csv_content, content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{form.slug}_submissions.csv"'
        return response
