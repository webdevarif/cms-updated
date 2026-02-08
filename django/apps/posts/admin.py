from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Comment, Post, PostMeta, PostType, Tag


@admin.register(PostType)
class PostTypeAdmin(admin.ModelAdmin):
    """
    Admin configuration for PostType model.
    """

    list_display = ["name", "key", "store", "is_builtin", "is_active", "post_count", "created_at"]
    list_filter = ["is_builtin", "is_active", "store", "created_at"]
    search_fields = ["name", "key", "description", "store__name"]
    readonly_fields = ["created_at", "updated_at", "post_count"]
    ordering = ["-is_builtin", "store__name", "name"]

    fieldsets = (
        (None, {"fields": ("store", "name", "key", "description")}),
        ("Settings", {"fields": ("is_builtin", "is_active", "schema")}),
        ("Statistics", {"fields": ("post_count",), "classes": ("collapse",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def post_count(self, obj):
        return obj.posts.count()

    post_count.short_description = "Post Count"

    def get_readonly_fields(self, request, obj=None):
        """
        Make builtin fields readonly.
        """
        readonly = list(self.readonly_fields)
        if obj and obj.is_builtin:
            readonly.extend(["name", "key", "is_builtin"])
        return readonly

    def has_delete_permission(self, request, obj=None):
        """
        Prevent deletion of builtin post types.
        """
        if obj and obj.is_builtin:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Admin configuration for Post model.
    """

    list_display = [
        "title",
        "slug",
        "post_type",
        "store",
        "status",
        "is_featured",
        "published_at",
        "created_at",
    ]
    list_filter = [
        "status",
        "is_featured",
        "content_type",
        "store",
        "post_type",
        "published_at",
        "created_at",
    ]
    search_fields = ["title", "slug", "excerpt", "content", "store__name", "post_type__name"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-published_at", "-created_at"]
    date_hierarchy = "published_at"

    fieldsets = (
        (None, {"fields": ("store", "post_type", "title", "slug")}),
        ("Content", {"fields": ("excerpt", "content", "content_type")}),
        ("Settings", {"fields": ("status", "is_featured", "published_at")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        """
        Optimize queryset with select_related.
        """
        return super().get_queryset(request).select_related("store", "post_type")

    def save_model(self, request, obj, form, change):
        """
        Auto-set published_at when publishing.
        """
        if obj.status == "published" and not obj.published_at:
            obj.published_at = obj.published_at or timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(PostMeta)
class PostMetaAdmin(admin.ModelAdmin):
    """
    Admin configuration for PostMeta model.
    """

    list_display = ["post", "key", "value_preview", "created_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["key", "post__title", "post__store__name"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    fieldsets = (
        (None, {"fields": ("post", "key", "value")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def value_preview(self, obj):
        """
        Show a preview of the JSON value.
        """
        value_str = str(obj.value)
        if len(value_str) > 50:
            return format_html('<span title="{}">{}</span>', value_str, value_str[:47] + "...")
        return value_str

    value_preview.short_description = "Value"

    def get_queryset(self, request):
        """
        Optimize queryset with select_related.
        """
        return super().get_queryset(request).select_related("post__store", "post__post_type")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for Category model.
    """

    list_display = ["name", "slug", "store", "parent", "is_active", "post_count", "created_at"]
    list_filter = ["is_active", "store", "parent", "created_at"]
    search_fields = ["name", "slug", "description", "store__name"]
    readonly_fields = ["created_at", "updated_at", "post_count", "full_path"]
    ordering = ["store__name", "name"]

    fieldsets = (
        (None, {"fields": ("store", "name", "slug", "description")}),
        ("Hierarchy", {"fields": ("parent", "full_path")}),
        ("Settings", {"fields": ("is_active",)}),
        ("Statistics", {"fields": ("post_count",), "classes": ("collapse",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def post_count(self, obj):
        return obj.posts.count()

    post_count.short_description = "Post Count"

    def get_queryset(self, request):
        """
        Optimize queryset with select_related.
        """
        return super().get_queryset(request).select_related("store", "parent")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin configuration for Tag model.
    """

    list_display = ["name", "slug", "store", "is_active", "post_count", "created_at"]
    list_filter = ["is_active", "store", "created_at"]
    search_fields = ["name", "slug", "description", "store__name"]
    readonly_fields = ["created_at", "updated_at", "post_count"]
    ordering = ["store__name", "name"]

    fieldsets = (
        (None, {"fields": ("store", "name", "slug", "description")}),
        ("Settings", {"fields": ("is_active",)}),
        ("Statistics", {"fields": ("post_count",), "classes": ("collapse",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def post_count(self, obj):
        return obj.posts.count()

    post_count.short_description = "Post Count"

    def get_queryset(self, request):
        """
        Optimize queryset with select_related.
        """
        return super().get_queryset(request).select_related("store")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Comment model.
    """

    list_display = [
        "user",
        "post_title",
        "content_preview",
        "store",
        "is_approved",
        "is_public",
        "is_reply",
        "created_at",
    ]
    list_filter = ["is_approved", "is_public", "store", "created_at", "post__post_type"]
    search_fields = ["content", "user__username", "user__email", "post__title"]
    readonly_fields = ["created_at", "updated_at", "is_reply"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        (None, {"fields": ("store", "post", "user", "parent")}),
        ("Content", {"fields": ("content",)}),
        ("Settings", {"fields": ("is_approved", "is_public", "is_reply")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def post_title(self, obj):
        return obj.post.title

    post_title.short_description = "Post"
    post_title.admin_order_field = "post__title"

    def content_preview(self, obj):
        content = obj.content
        return content[:50] + "..." if len(content) > 50 else content

    content_preview.short_description = "Content"

    def get_queryset(self, request):
        """
        Optimize queryset with select_related.
        """
        return super().get_queryset(request).select_related("store", "post", "user", "parent")
