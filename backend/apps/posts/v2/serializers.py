"""
Serializers for posts app.
"""
from rest_framework import serializers
from ..models import Post, PostType, Taxonomy, Term


class PostTypeSerializer(serializers.ModelSerializer):
    """Serializer for PostType model"""
    
    class Meta:
        model = PostType
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post model with translation support"""
    post_type_name = serializers.CharField(source='post_type.name', read_only=True)
    author_email = serializers.EmailField(source='author.email', read_only=True)
    featured_image_url = serializers.SerializerMethodField()
    translated_title = serializers.SerializerMethodField()
    translated_content = serializers.SerializerMethodField()
    translated_excerpt = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'post_type', 'post_type_name',
            'author', 'author_email', 'featured_image', 'featured_image_url',
            'status', 'published_at', 'scheduled_at',
            'meta_title', 'meta_description', 'meta_keywords',
            'categories', 'tags', 'custom_fields',
            'translated_title', 'translated_content', 'translated_excerpt',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'published_at', 'author'
        ]
    
    def get_featured_image_url(self, obj):
        """Get featured image URL"""
        if obj.featured_image:
            return obj.featured_image.get_absolute_url()
        return None
    
    def get_translated_field(self, obj, field_name):
        """Get translated field"""
        request = self.context.get('request')
        if not request:
            return getattr(obj, field_name)
        
        language_code = getattr(request, 'LANGUAGE_CODE', 'en')
        store = getattr(request, 'store', None)
        
        # Generate translation key
        key = f"posts.{field_name}.{obj.id}"
        
        from apps.public.translations.services import TranslationService
        return TranslationService.get_translation(key, language_code, store, getattr(obj, field_name))
    
    def get_translated_title(self, obj):
        """Get translated title"""
        return self.get_translated_field(obj, 'title')
    
    def get_translated_content(self, obj):
        """Get translated content"""
        return self.get_translated_field(obj, 'content')
    
    def get_translated_excerpt(self, obj):
        """Get translated excerpt"""
        return self.get_translated_field(obj, 'excerpt')


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating posts"""
    
    class Meta:
        model = Post
        fields = [
            'title', 'slug', 'content', 'excerpt', 'post_type',
            'featured_image', 'meta_title', 'meta_description', 'meta_keywords',
            'categories', 'tags', 'custom_fields'
        ]


class TaxonomySerializer(serializers.ModelSerializer):
    """Serializer for Taxonomy model"""
    term_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Taxonomy
        fields = [
            'id', 'name', 'slug', 'taxonomy_type', 'store',
            'description', 'term_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class TaxonomyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating taxonomies"""
    
    class Meta:
        model = Taxonomy
        fields = ['name', 'slug', 'taxonomy_type', 'description']


class TermSerializer(serializers.ModelSerializer):
    """Serializer for Term model"""
    post_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Term
        fields = [
            'id', 'name', 'slug', 'taxonomy', 'parent',
            'description', 'post_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class TermCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating terms"""
    
    class Meta:
        model = Term
        fields = ['name', 'slug', 'taxonomy', 'parent', 'description']
