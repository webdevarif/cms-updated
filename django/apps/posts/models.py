from apps.stores.models import Store

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class PostType(models.Model):
    """
    Represents a custom post type (blog post, page, product, etc.) scoped by store.
    """

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="post_types")
    name = models.CharField(max_length=100)
    key = models.SlugField(
        max_length=50, help_text="Unique identifier for this post type within the store"
    )
    description = models.TextField(blank=True, help_text="Optional description of this post type")
    is_builtin = models.BooleanField(
        default=False, help_text="System post types that cannot be deleted"
    )
    is_active = models.BooleanField(default=True, help_text="Whether this post type is active")
    schema = models.JSONField(
        blank=True, null=True, help_text="JSON schema for custom fields (future use)"
    )

    # Feature flags to control what features are available per post type
    allow_categories = models.BooleanField(
        default=True, help_text="Whether posts of this type can have categories"
    )
    allow_tags = models.BooleanField(
        default=True, help_text="Whether posts of this type can have tags"
    )
    allow_comments = models.BooleanField(
        default=True, help_text="Whether posts of this type can have comments"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["store", "key"]
        ordering = ["-is_builtin", "name"]
        verbose_name = "Post Type"
        verbose_name_plural = "Post Types"

    def __str__(self):
        return f"{self.store.name}: {self.name}"

    def clean(self):
        if self.is_builtin and self.key not in ["post", "page", "blog", "policy"]:
            raise ValidationError(
                "Builtin post types can only have keys 'post', 'page', 'blog', or 'policy'"
            )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = slugify(self.name)
        self.clean()
        super().save(*args, **kwargs)


class Post(models.Model):
    """
    Content entry under a PostType, scoped by store.
    """

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    CONTENT_TYPE_CHOICES = [
        ("html", "HTML"),
        ("markdown", "Markdown"),
        ("json", "JSON"),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="posts")
    post_type = models.ForeignKey(PostType, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, help_text="URL-friendly identifier")
    excerpt = models.TextField(blank=True, help_text="Short summary or excerpt")
    content = models.TextField(blank=True, help_text="Main content (HTML, Markdown, or JSON)")
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default="html")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    is_featured = models.BooleanField(default=False, help_text="Whether this post is featured")
    categories = models.ManyToManyField("posts.Category", related_name="posts", blank=True)
    tags = models.ManyToManyField("posts.Tag", related_name="posts", blank=True)

    # User tracking fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_posts",
        help_text="User who created this post",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_posts",
        help_text="User who last updated this post",
    )

    published_at = models.DateTimeField(
        null=True, blank=True, help_text="When this post was published"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["store", "post_type", "slug"]
        ordering = ["-published_at", "-created_at"]
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.title

    def clean(self):
        # Auto-set published_at when status changes to published
        if self.status == "published" and not self.published_at:
            self.published_at = timezone.now()
        elif self.status != "published":
            self.published_at = None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_published(self):
        return self.status == "published" and (
            self.published_at is None or self.published_at <= timezone.now()
        )


class PostMeta(models.Model):
    """
    Key/value metadata for posts to support custom fields and future extensibility.
    """

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="meta")
    key = models.CharField(max_length=100, help_text="Metadata key")
    value = models.JSONField(help_text="Metadata value (can be string, number, object, etc.)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["post", "key"]
        ordering = ["key"]
        verbose_name = "Post Meta"
        verbose_name_plural = "Post Meta"

    def __str__(self):
        return f"{self.post.title}: {self.key}"


class Category(models.Model):
    """
    Categories for organizing posts, scoped by store with simple hierarchy support.
    """

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, help_text="URL-friendly identifier")
    description = models.TextField(blank=True, help_text="Optional category description")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    is_active = models.BooleanField(default=True, help_text="Whether this category is active")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["store", "slug"]
        ordering = ["name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.store.name}: {self.name}"

    def clean(self):
        # Prevent circular references in parent hierarchy
        if self.parent and self.parent == self:
            raise ValidationError("A category cannot be its own parent")
        if self.parent and self.parent.parent == self:
            raise ValidationError("Circular reference in category hierarchy")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.clean()
        super().save(*args, **kwargs)

    @property
    def full_path(self):
        """
        Return the full path including parent categories.
        """
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name


class Tag(models.Model):
    """
    Tags for labeling posts, scoped by store.
    """

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, help_text="URL-friendly identifier")
    description = models.TextField(blank=True, help_text="Optional tag description")
    is_active = models.BooleanField(default=True, help_text="Whether this tag is active")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["store", "slug"]
        ordering = ["name"]
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return f"{self.store.name}: {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Comment(models.Model):
    """
    Comments on posts with optional threading support.
    """

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    content = models.TextField(help_text="Comment content")
    is_approved = models.BooleanField(default=True, help_text="Whether this comment is approved")
    is_public = models.BooleanField(default=True, help_text="Whether this comment is public")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.user.get_full_name() or self.user.username} on {self.post.title}"

    def clean(self):
        # Ensure comment store matches post store
        if self.post and self.post.store != self.store:
            raise ValidationError("Comment store must match post store")

        # Prevent replies to replies beyond one level for simplicity
        if self.parent and self.parent.parent:
            raise ValidationError("Comments can only be nested one level deep")

    def save(self, *args, **kwargs):
        if self.post:
            self.store = self.post.store
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_reply(self):
        """Check if this is a reply to another comment."""
        return self.parent is not None


class PostTypeTemplate(models.Model):
    """
    Stores which themes.Template is used for a given PostType under a given Theme.
    This does NOT replace themes.Template; it just points to it.
    """

    store = models.ForeignKey(
        "stores.Store", on_delete=models.CASCADE, related_name="post_type_templates"
    )
    post_type = models.ForeignKey(
        "posts.PostType", on_delete=models.CASCADE, related_name="theme_templates"
    )
    theme = models.ForeignKey(
        "themes.Theme", on_delete=models.CASCADE, related_name="post_type_templates"
    )
    template = models.ForeignKey(
        "themes.Template", on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = [("store", "post_type", "theme")]
        ordering = ["post_type__name", "theme__name"]
        verbose_name = "Post Type Template"
        verbose_name_plural = "Post Type Templates"

    def __str__(self):
        template_name = self.template.name if self.template else "No template"
        return f"{self.store.name}: {self.post_type.name} → {self.theme.name} ({template_name})"

    def clean(self):
        """Validate that template belongs to the theme if set"""
        if self.template and self.template.theme != self.theme:
            raise ValidationError("Template must belong to the selected theme")

        # Ensure theme and store consistency
        if self.theme and hasattr(self.theme, "store") and self.theme.store != self.store:
            raise ValidationError("Theme must belong to the same store")
