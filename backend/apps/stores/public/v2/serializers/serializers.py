"""
Public stores serializers.
"""
from rest_framework import serializers
from apps.stores.models import Store


class StorePublicSerializer(serializers.ModelSerializer):
    """Public store information"""

    class Meta:
        model = Store
        fields = [
            'id', 'name', 'slug', 'domain', 'description', 'logo',
            'status', 'store_type', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
