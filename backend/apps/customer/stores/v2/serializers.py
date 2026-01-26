"""
Customer stores serializers.
"""
from apps.stores.serializers_v2 import BaseStoreSerializer, BaseStorePublicSerializer, BaseStoreSettingsSerializer


class StoreCustomerSerializer(BaseStoreSerializer):
    """Serializer for Store model in customer context"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove owner field for customer context (user is always current user)
        if 'owner' in self.fields:
            del self.fields['owner']
        # Remove access_code field for customer context
        if 'access_code' in self.fields:
            del self.fields['access_code']


class StoreSettingsCustomerSerializer(BaseStoreSettingsSerializer):
    """Store settings serializer in customer context"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove status field for customer context (users can't change status)
        if 'status' in self.fields:
            del self.fields['status']
        # Remove store_type field for customer context (users can't change type)
        if 'store_type' in self.fields:
            del self.fields['store_type']
