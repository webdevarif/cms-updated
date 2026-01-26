"""
Customer entities serializers - authenticated interface for entity interactions.
"""
from rest_framework import serializers
from apps.entities.models import EntityAction, EntityInteraction


class CustomerEntityActionSerializer(serializers.ModelSerializer):
    """Customer entity action serializer."""
    
    user_interaction_count = serializers.SerializerMethodField()
    has_user_interaction = serializers.SerializerMethodField()
    
    class Meta:
        model = EntityAction
        fields = [
            'id', 'name', 'slug', 'description', 'action_type', 'icon', 'color',
            'is_public', 'allow_anonymous', 'user_interaction_count', 'has_user_interaction'
        ]
        read_only_fields = fields
    
    def get_user_interaction_count(self, obj):
        """Get current user's interaction count for this action."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return EntityInteraction.objects.filter(
                action=obj,
                user=request.user,
                is_active=True
            ).count()
        return 0
    
    def get_has_user_interaction(self, obj):
        """Check if current user has interacted with this action."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return EntityInteraction.objects.filter(
                action=obj,
                user=request.user,
                is_active=True
            ).exists()
        return False


class CustomerEntityInteractionSerializer(serializers.ModelSerializer):
    """Customer entity interaction serializer."""
    
    action_name = serializers.CharField(source='action.name', read_only=True)
    action_slug = serializers.CharField(source='action.slug', read_only=True)
    action_type = serializers.CharField(source='action.action_type', read_only=True)
    action_icon = serializers.CharField(source='action.icon', read_only=True)
    action_color = serializers.CharField(source='action.color', read_only=True)
    content_type_name = serializers.CharField(source='content_type.model', read_only=True)
    
    class Meta:
        model = EntityInteraction
        fields = [
            'id', 'action', 'action_name', 'action_slug', 'action_type', 'action_icon', 'action_color',
            'content_type', 'object_id', 'content_type_name', 'value', 'rating',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'action', 'created_at', 'updated_at'
        ]


class CustomerEntityInteractionCreateSerializer(serializers.ModelSerializer):
    """Customer entity interaction creation serializer."""
    
    class Meta:
        model = EntityInteraction
        fields = [
            'content_type', 'object_id', 'value', 'rating'
        ]
    
    def validate_content_type(self, value):
        """Validate content type exists."""
        try:
            ContentType.objects.get(id=value)
        except ContentType.DoesNotExist:
            raise serializers.ValidationError("Invalid content type")
        return value
    
    def validate_rating(self, value):
        """Validate rating is within valid range."""
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def validate(self, data):
        """Validate interaction data based on action type."""
        # This would need the action to be passed in context
        # For now, basic validation
        return data


class CustomerEntityStatsSerializer(serializers.Serializer):
    """Customer entity statistics serializer."""
    
    name = serializers.CharField(read_only=True)
    action_type = serializers.CharField(read_only=True)
    count = serializers.IntegerField(read_only=True)
    total_rating = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
