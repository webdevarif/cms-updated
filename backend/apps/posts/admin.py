"""
Admin configuration for posts app.
"""
from django.contrib import admin
from .v2.models import Post, PostType, Taxonomy, Term


@admin.register(PostType)
class PostTypeAdmin(admin.ModelAdmin):
    """Admin interface for PostType model"""
    list_display = ['name', 'slug', 'store', 'is_public', 'is_hierarchical']
    list_filter = ['is_public', 'is_hierarchical', 'store']
    search_fields = ['name', 'slug']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin interface for Post model"""
    list_display = ['title', 'slug', 'post_type', 'status', 'author', 'store', 'published_at']
    list_filter = ['status', 'post_type', 'store', 'published_at']
    search_fields = ['title', 'slug', 'content']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'published_at'


@admin.register(Taxonomy)
class TaxonomyAdmin(admin.ModelAdmin):
    """Admin interface for Taxonomy model"""
    list_display = ['name', 'slug', 'taxonomy_type', 'store']
    list_filter = ['taxonomy_type', 'store']
    search_fields = ['name', 'slug']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    """Admin interface for Term model"""
    list_display = ['name', 'slug', 'taxonomy', 'parent']
    list_filter = ['taxonomy']
    search_fields = ['name', 'slug']
    readonly_fields = ['created_at', 'updated_at']
