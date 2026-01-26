"""
Public themes serializers.
"""
from apps.themes.models import Theme


class ThemePublicSerializer(serializers.ModelSerializer):
    """Public theme serializer"""
    
    class Meta:
        model = Theme
        fields = [
            'id', 'name', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ColorSchemePublicSerializer(serializers.Serializer):
    """Color scheme serializer for public context"""
    
    class Meta:
        fields = ['name', 'colors', 'fonts', 'spacing', 'border_radius', 'shadows']


class TemplatePublicSerializer(serializers.ModelSerializer):
    """Public template serializer"""
    
    class Meta:
        model = Template
        fields = [
            'id', 'name', 'key', 'template_role', 'description', 'content', 'variables'
        ]
        read_only_fields = ['id']
