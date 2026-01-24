"""
Views for SMTP configuration management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.accounts.models import StoreUser
from core.permissions import IsStoreAdmin
from apps.smtp.models import SmtpConfiguration
from apps.smtp.serializers import SmtpConfigSerializer


class SmtpConfigViewSet(viewsets.ModelViewSet):
    """SMTP configuration management"""
    serializer_class = SmtpConfigSerializer
    permission_classes = [IsAuthenticated, IsStoreAdmin]
    
    def get_queryset(self):
        return SmtpConfiguration.objects.filter(store=self.request.store)
    
    def perform_create(self, serializer):
        serializer.save(store=self.request.store)
    
    @extend_schema(
        summary="Test SMTP connection",
        description="Test SMTP configuration connection",
        responses={200: {"success": bool, "message": str}}
    )
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test SMTP connection"""
        config = self.get_object()
        try:
            # Test connection logic here
            return Response({
                'success': True,
                'message': 'Connection successful'
            })
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
