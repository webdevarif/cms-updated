"""
Dashboard translations API views.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class TranslationDashboardViewSet(viewsets.ViewSet):
    """
    Dashboard translations API placeholder.
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Placeholder list method"""
        return Response({"message": "Translations API not implemented yet"})

    def retrieve(self, request, pk=None):
        """Placeholder retrieve method"""
        return Response({"message": "Translations API not implemented yet"})
