"""
Public stores API views.
"""
from apps.stores.models import Store
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..serializers.serializers import StorePublicSerializer


class StorePublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public store API - no authentication required.
    Provides read-only access to active stores for discovery.
    """

    permission_classes = [permissions.AllowAny]
    queryset = Store.objects.filter(status="active")
    serializer_class = StorePublicSerializer

    def get_queryset(self):
        """Filter by domain or subdomain"""
        queryset = super().get_queryset()

        # Filter by domain if provided
        domain = self.request.GET.get("domain")
        if domain:
            queryset = queryset.filter(domain=domain)

        # Filter by subdomain if provided
        subdomain = self.request.GET.get("subdomain")
        if subdomain:
            queryset = queryset.filter(slug=subdomain)

        return queryset

    @extend_schema(summary="List stores", description="List active stores")
    def list(self, request, *args, **kwargs):
        """List stores"""
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Get store", description="Get store details")
    def retrieve(self, request, *args, **kwargs):
        """Get store details"""
        return super().retrieve(request, *args, **kwargs)


class StoreVerificationViewSet(viewsets.ViewSet):
    """
    Public store verification endpoints.
    """

    permission_classes = []

    @action(detail=False, methods=["post"])
    def verify_store(self, request):
        """Verify store using verification token"""
        token = request.data.get("token")
        if not token:
            return Response(
                {"error": "Verification token is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from apps.stores.services import StoreAccessService

            store = StoreAccessService.verify_store(token)

            return Response(
                {
                    "message": f'Store "{store.name}" has been successfully verified and activated!',
                    "store_id": store.id,
                    "store_name": store.name,
                    "redirect_url": f"/stores/{store.slug}/dashboard",
                }
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
