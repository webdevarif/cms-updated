"""
Base views for posts app.
"""
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class StoreScopedViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet that automatically filters by store.
    All ViewSets must inherit from this and filter by request.store
    """
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request, 'store'):
            return queryset.filter(store=self.request.store)
        return queryset.none()
    
    def perform_create(self, serializer):
        if hasattr(self.request, 'store'):
            serializer.save(store=self.request.store)
        else:
            raise PermissionDenied("Store context is required")
