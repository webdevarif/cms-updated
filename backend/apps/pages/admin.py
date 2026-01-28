"""
Pages admin configuration.
"""
from django.contrib import admin

from .models import Post, PostType, Taxonomy, Term


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Post admin configuration"""

    list_display = ["title", "slug", "post_type", "store", "status", "created_at"]
    list_filter = ["status", "post_type", "store", "created_at"]
    search_fields = ["title", "content", "slug"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    ordering = ["-created_at"]


@admin.register(PostType)
class PostTypeAdmin(admin.ModelAdmin):
    """Post type admin configuration"""

    list_display = ["name", "slug", "store", "is_public", "created_at"]
    list_filter = ["is_public", "is_system", "created_at"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Taxonomy)
class TaxonomyAdmin(admin.ModelAdmin):
    """Taxonomy admin configuration"""

    list_display = ["name", "slug", "taxonomy_type", "store", "created_at"]
    list_filter = ["taxonomy_type", "store", "created_at"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    """Term admin configuration"""

    list_display = ["name", "slug", "taxonomy", "store", "parent", "created_at"]
    list_filter = ["taxonomy", "store", "created_at"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
