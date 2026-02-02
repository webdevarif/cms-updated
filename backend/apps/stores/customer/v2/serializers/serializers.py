"""
Customer stores serializers.
"""

from apps.stores.models import Store
from rest_framework import serializers


class StoreCustomerSerializer(serializers.ModelSerializer):
    """Customer store management"""

    class Meta:
        model = Store
        fields = [
            "id",
            "name",
            "slug",
            "domain",
            "description",
            "logo",
            "favicon",
            "status",
            "store_type",
            "verification_token",
            "access_code",
            "meta_title",
            "meta_description",
            "meta_keywords",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "verification_token",
            "access_code",
            "created_at",
            "updated_at",
        ]
