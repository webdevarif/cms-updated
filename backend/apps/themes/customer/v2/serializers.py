"""
Customer themes serializers.
"""

from apps.themes.models import Theme
from rest_framework import serializers


class ThemeCustomerSerializer(serializers.ModelSerializer):
    """Customer theme information"""

    class Meta:
        model = Theme
        fields = [
            "id",
            "name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
