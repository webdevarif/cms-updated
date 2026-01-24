"""
API views for queue module.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from rest_framework import viewsets
from core.permissions import IsStoreOwner
from ..models import QueueTask
from .serializers import QueueTaskSerializer


class QueueTaskViewSet(viewsets.ModelViewSet):
    """
    Queue task management endpoints
    """
    permission_classes = [IsAuthenticated, IsStoreOwner]
    serializer_class = QueueTaskSerializer
    
    def get_queryset(self):
        return QueueTask.objects.filter(store=self.request.store)
    
    @extend_schema(
        summary="Get Task Status",
        description="Get task status by task_id",
        responses={200: None}
    )
    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get task status"""
        from ..services import QueueService
        
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response(
                {'error': 'task_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task_status = QueueService.get_task_status(task_id)
        if task_status:
            return Response(task_status)
        
        return Response(
            {'error': 'Task not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @extend_schema(
        summary="Retry Task",
        description="Retry a failed task",
        responses={200: None}
    )
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed task"""
        from ..services import QueueService
        
        task = self.get_object()
        success = QueueService.retry_task(task.task_id)
        
        if success:
            return Response({'message': 'Task queued for retry'})
        
        return Response(
            {'error': 'Max retries exceeded or task not found'},
            status=status.HTTP_400_BAD_REQUEST
        )
