"""
Dashboard stores serializers.
"""
from apps.stores.serializers_v2 import BaseStoreSerializer, BaseStoreCreateSerializer, BaseStoreSettingsSerializer


class StoreDashboardSerializer(BaseStoreSerializer):
    """Serializer for Store model in dashboard context"""
    owner_email = serializers.EmailField(source='owner.email', read_only=True)


class StoreCreateDashboardSerializer(BaseStoreCreateSerializer):
    """Store creation serializer in dashboard context"""
    pass


class StoreSettingsDashboardSerializer(BaseStoreSettingsSerializer):
    """Store settings serializer in dashboard context"""
    pass
