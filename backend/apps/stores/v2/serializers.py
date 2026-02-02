"""
Stores V2 API serializers.
Consolidated serializers from public, customer, and dashboard layers.
"""

from apps.stores.models import Store, StoreSettings
from rest_framework import serializers


class StorePublicSerializer(serializers.ModelSerializer):
    """Public store information"""

    class Meta:
        model = Store
        fields = [
            "id",
            "name",
            "slug",
            "domain",
            "description",
            "logo",
            "status",
            "store_type",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StoreCustomerSerializer(serializers.ModelSerializer):
    """Customer store serializer for store owners"""

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
            "google_analytics_id",
            "facebook_pixel_id",
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

    def create(self, validated_data):
        """Create store and initialize settings"""
        from apps.stores.services import StoreService

        return StoreService.create_store(self.context["request"].user, validated_data)


class StoreDashboardSerializer(serializers.ModelSerializer):
    """Dashboard store serializer with full access"""

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
            "google_analytics_id",
            "facebook_pixel_id",
            "created_at",
            "updated_at",
            "last_accessed",
        ]
        read_only_fields = [
            "id",
            "verification_token",
            "access_code",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        """Create store and initialize settings"""
        from apps.stores.services import StoreService

        return StoreService.create_store(self.context["request"].user, validated_data)


class StoreSettingsSerializer(serializers.ModelSerializer):
    """Store settings serializer"""

    class Meta:
        model = StoreSettings
        fields = [
            "site_name",
            "site_description",
            "contact_email",
            "phone",
            "address",
            "city",
            "state",
            "country",
            "postal_code",
            "currency",
            "timezone",
            "language",
            "tax_rate",
            "shipping_enabled",
            "free_shipping_threshold",
            "logo",
            "favicon",
            "custom_settings",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
