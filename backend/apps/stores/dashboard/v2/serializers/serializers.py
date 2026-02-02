"""
Dashboard stores serializers.
"""

from apps.metafields.services import serialize_metafields_for_instance
from apps.stores.models import Store, StoreSettings
from rest_framework import serializers


class StoreDashboardSerializer(serializers.ModelSerializer):
    """Dashboard store management"""

    metafields = serializers.SerializerMethodField(read_only=True)

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
            "metafields",
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

    def get_metafields(self, obj):
        """Return standardized metafields for the store"""
        return serialize_metafields_for_instance(obj)


class StoreSettingsSerializer(serializers.ModelSerializer):
    """Store settings management"""

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
