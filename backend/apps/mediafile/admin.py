"""
Admin configuration for media app.
"""

from django.contrib import admin

from .models.media_file import MediaFile
from .models.media_folder import MediaFolder


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    """Admin interface for MediaFile model"""

    list_display = [
        "original_filename",
        "resource_type",
        "file_size_formatted",
        "store",
        "folder",
        "created_at",
    ]
    list_filter = ["resource_type", "store", "folder", "created_at"]
    search_fields = ["original_filename", "alt_text", "description"]
    readonly_fields = ["created_at", "updated_at", "file_size_formatted"]
    date_hierarchy = "created_at"


@admin.register(MediaFolder)
class MediaFolderAdmin(admin.ModelAdmin):
    """Admin interface for MediaFolder model"""

    list_display = ["name", "slug", "store", "parent", "created_at"]
    list_filter = ["store", "parent", "created_at"]
    search_fields = ["name", "slug"]
    readonly_fields = ["slug", "created_at", "updated_at"]
    date_hierarchy = "created_at"
