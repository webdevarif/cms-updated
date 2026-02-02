"""
Customer stores API views.
"""

from apps.stores.models import Store
from apps.stores.services import StoreAccessService, StoreService
from core.permissions import IsStoreUser
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..serializers.serializers import StoreCustomerSerializer


class StoreCustomerViewSet(viewsets.ModelViewSet):
    """
    Customer store API - authenticated users manage their own stores.
    """

    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = StoreCustomerSerializer

    def get_queryset(self):
        """Filter to user's own stores"""
        return Store.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """Set owner when creating store"""
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def verify_email(self, request, pk=None):
        """Verify store email with token"""
        store = self.get_object()
        token = request.data.get("token")

        if StoreService.verify_store(store, token):
            return Response({"message": "Store verified successfully"})
        return Response({"error": "Invalid verification token"}, status=status.HTTP_400_BAD_REQUEST)


class StoreAccessViewSet(viewsets.ViewSet):
    """
    Store access management for authenticated users.
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def request_access(self, request):
        """Request a store access code"""
        # Generate access code for user
        access_code = StoreAccessService.generate_access_code()

        # Create a placeholder store request (or just return the code)
        # In a real implementation, this might send an email or create a request record

        return Response(
            {
                "access_code": access_code,
                "message": "Access code generated. Use this code to create your store.",
                "expires_in": "24 hours",  # Could be configurable
            }
        )

    @action(detail=False, methods=["post"])
    def validate_code(self, request):
        """Validate an access code"""
        access_code = request.data.get("access_code")
        if not access_code:
            return Response(
                {"error": "Access code is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validated_request = StoreAccessService.validate_access_code(access_code, request.user)
            return Response({"valid": True, "message": "Access code is valid"})
        except Exception as e:
            return Response({"valid": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def create_store(self, request):
        """Create store with access code validation"""
        access_code = request.data.get("access_code")
        store_data = request.data.get("store_data", {})

        if not access_code:
            return Response(
                {"error": "Access code is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            store = StoreAccessService.create_store_request(request.user, store_data, access_code)
            return Response(
                {
                    "store_id": store.id,
                    "name": store.name,
                    "status": store.status,
                    "message": "Store created successfully. Check your email for verification instructions.",
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def my_codes(self, request):
        """Get current user's access codes"""
        # Get stores that have access codes for this user
        stores = Store.objects.filter(owner=request.user).exclude(access_code="")

        codes = []
        for store in stores:
            codes.append(
                {
                    "store_id": store.id,
                    "store_name": store.name,
                    "access_code": store.access_code,
                    "status": store.status,
                    "created_at": store.created_at,
                }
            )

        return Response({"access_codes": codes})
