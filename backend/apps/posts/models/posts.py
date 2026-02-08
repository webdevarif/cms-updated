"""
Posts models - PostType, Post, Taxonomy, Term, PostRevision.
"""

from core.models import TenantModel

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify

User = get_user_model()


class PostType(TenantModel):
    """Define content types (blog, page, or custom)"""

    BUILTIN_TYPES = ["post", "page"]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    is_public = models.BooleanField(default=True)
    is_hierarchical = models.BooleanField(default=False)
    supports_comments = models.BooleanField(default=True)
    supports_featured_image = models.BooleanField(default=True)
    supports_excerpt = models.BooleanField(default=True)
    supports_custom_fields = models.BooleanField(default=True)

    # System fields for bootstrap
    is_system = models.BooleanField(default=False)
    is_deletable = models.BooleanField(default=True)

    # Taxonomy support
    supports_categories = models.BooleanField(default=True)
    supports_tags = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = "posts_post_type"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_system"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Post(TenantModel):
    """Unified post model for all content types"""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("scheduled", "Scheduled"),
        ("private", "Private"),
        ("trash", "Trash"),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, db_index=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True)

    # Relationships
    post_type = models.ForeignKey(PostType, on_delete=models.CASCADE, related_name="posts")
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="posts")
    featured_image = models.ForeignKey(
        "mediafile.MediaFile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="featured_posts",
    )

    # Status and publishing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    published_at = models.DateTimeField(null=True, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)

    # SEO
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)

    # Taxonomy
    categories = models.ManyToManyField("Taxonomy", related_name="posts", blank=True)
    tags = models.ManyToManyField("Term", related_name="tagged_posts", blank=True)

    # Custom fields
    custom_fields = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = "posts_post"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["status", "published_at"]),
            models.Index(fields=["post_type"]),
            models.Index(fields=["published_at"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @classmethod
    def set_featured_image_from_upload(cls, post, uploaded_file, uploaded_by=None):
        """Set featured image using MediaService upload"""
        from apps.mediafile.services.media_service import MediaService

        media_service = MediaService()
        media_file = media_service.upload_from_request(
            store=post.store,
            file_obj=uploaded_file,
            uploaded_by=uploaded_by,
            folder_name="featured_images",
            alt_text=f"Featured image for {post.title}",
            description=f"Featured image for post: {post.title}",
        )

        post.featured_image = media_file
        post.save(update_fields=["featured_image"])
        return media_file

    def toggle_like(self, user):
        """Toggle post like using EntityService"""
        from apps.entities.v2.services import EntityService

        return EntityService.toggle_action(
            user=user, content_object=self, action_slug="like", store=self.store
        )

    def get_like_count(self):
        """Get total likes using EntityService"""
        from apps.entities.v2.services import EntityService

        return EntityService.get_interaction_count(
            content_object=self, action_slug="like", store=self.store
        )

    def user_liked(self, user):
        """Check if user liked this post using EntityService"""
        from apps.entities.v2.services import EntityService

        interactions = EntityService.get_user_interactions(
            user=user, content_object=self, store=self.store
        )
        return interactions.filter(action__slug="like").exists()


class Taxonomy(TenantModel):
    """Categories, Tags, and custom taxonomies"""

    TAXONOMY_TYPES = [
        ("category", "Category"),
        ("tag", "Tag"),
        ("custom", "Custom"),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    taxonomy_type = models.CharField(max_length=20, choices=TAXONOMY_TYPES)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = "posts_taxonomy"
        ordering = ["name"]
        unique_together = ("slug",)
        indexes = [
            models.Index(fields=["taxonomy_type"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Term(TenantModel):
    """Taxonomy terms (individual categories/tags)"""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    taxonomy = models.ForeignKey(Taxonomy, on_delete=models.CASCADE, related_name="terms")
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(TenantModel.Meta):
        db_table = "posts_term"
        ordering = ["name"]
        unique_together = ("slug",)
        indexes = [
            models.Index(fields=["taxonomy"]),
            models.Index(fields=["parent"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class PostRevision(models.Model):
    """Track revision history for posts"""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="revisions")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)
    revision_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "posts_post_revision"
        ordering = ["-revision_number"]
        indexes = [
            models.Index(fields=["post", "revision_number"]),
            models.Index(fields=["created_at"]),
        ]
        unique_together = ("post", "revision_number")

    def __str__(self):
        return f"Revision {self.revision_number} of {self.post.title}"
