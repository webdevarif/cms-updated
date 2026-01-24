"""
API views for test module.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema

from ..models import TestRun
from .serializers import TestRunSerializer
from ..services import TestRunnerService


class TestRunViewSet(viewsets.ModelViewSet):
    """
    Test run management endpoints
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = TestRun.objects.all()
    serializer_class = TestRunSerializer
    
    @extend_schema(
        summary="Run all tests",
        description="Run all tests for the store",
        responses={200: TestRunSerializer}
    )
    @action(detail=False, methods=['post'])
    def run_all(self, request):
        """Run all tests for the store"""
        from ..runners.global_runner import GlobalTestRunner
        
        runner = GlobalTestRunner(store=request.store, initiated_by=request.user)
        test_run = runner.run_all_tests()
        
        serializer = self.get_serializer(test_run)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Run specific tests",
        description="Run specific tests by app/endpoint",
        request=None,
        responses={200: TestRunSerializer}
    )
    @action(detail=False, methods=['post'])
    def run_specific(self, request):
        """Run specific tests"""
        test_spec = request.data.get('tests', [])
        runner = GlobalTestRunner(store=request.store, initiated_by=request.user)
        test_run = runner.run_specific_tests(test_spec)
        
        serializer = self.get_serializer(test_run)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get test history",
        description="Get recent test run history",
        responses={200: TestRunSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get test run history"""
        limit = int(request.query_params.get('limit', 10))
        test_runs = TestRunnerService.get_test_history(store=request.store, limit=limit)
        
        serializer = self.get_serializer(test_runs, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get test statistics",
        description="Get test statistics",
        responses={200: None}
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get test statistics"""
        days = int(request.query_params.get('days', 30))
        stats = TestRunnerService.get_test_stats(store=request.store, days=days)
        
        return Response(stats)
