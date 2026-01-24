"""
Serializers for test module.
"""
from rest_framework import serializers
from ..models import TestRun, TestResult


class TestRunSerializer(serializers.ModelSerializer):
    """Serializer for TestRun"""
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = TestRun
        fields = '__all__'
        read_only_fields = ['id', 'started_at', 'completed_at']
    
    def get_success_rate(self, obj):
        return obj.success_rate


class TestResultSerializer(serializers.ModelSerializer):
    """Serializer for TestResult"""
    
    class Meta:
        model = TestResult
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
